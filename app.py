import streamlit as st
import fitz  
import pandas as pd
import re
import math
import google.generativeai as genai
from datetime import datetime, timedelta
from collections import deque

# --- Rate Limiter Class ---
class RateLimiter:
    def __init__(self, max_requests=15, time_window=60):
        """
        max_requests: Maximum number of requests allowed
        time_window: Time window in seconds (default 60s = 1 minute)
        """
        if 'request_times' not in st.session_state:
            st.session_state.request_times = deque()
        self.max_requests = max_requests
        self.time_window = time_window
    
    def can_make_request(self):
        """Check if a new request can be made"""
        now = datetime.now()
        # Remove requests older than time window
        while st.session_state.request_times and \
              (now - st.session_state.request_times[0]).total_seconds() > self.time_window:
            st.session_state.request_times.popleft()
        
        return len(st.session_state.request_times) < self.max_requests
    
    def add_request(self):
        """Record a new request"""
        st.session_state.request_times.append(datetime.now())
    
    def get_wait_time(self):
        """Get seconds until next request is allowed"""
        if len(st.session_state.request_times) < self.max_requests:
            return 0
        
        oldest_request = st.session_state.request_times[0]
        elapsed = (datetime.now() - oldest_request).total_seconds()
        return max(0, self.time_window - elapsed)
    
    def get_remaining_requests(self):
        """Get number of remaining requests in current window"""
        now = datetime.now()
        # Clean old requests
        while st.session_state.request_times and \
              (now - st.session_state.request_times[0]).total_seconds() > self.time_window:
            st.session_state.request_times.popleft()
        
        return self.max_requests - len(st.session_state.request_times)

# Initialize rate limiter (15 requests per minute)
rate_limiter = RateLimiter(max_requests=15, time_window=60)

# --- UI 样式 ---
st.markdown("""
    <style>
        .stApp {
            background-image: url("https://github.com/USAGI7878/Blood-report_kt-v/raw/main/background%20ver%202.png");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .block-container {
            background-color: rgba(20, 20, 20, 0.85);
            border-radius: 15px;
            padding: 2rem;
            color: white;
        }
        .stTitle, .stSubheader, .stDataFrame, .stText, .stMetric {
            color: white;
        }
        .stButton > button {
            background-color: #555;
            color: white;
        }
        .stRadio > div > label {
            color: white;
        }
        .stFileUploader > div {
            color: white;
        }
        .ai-suggestion {
            background-color: rgba(40, 90, 140, 0.6);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
            margin: 1rem 0;
        }
        .warning-box {
            background-color: rgba(140, 40, 40, 0.6);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #ff6b6b;
            margin: 0.5rem 0;
        }
        .rate-limit-info {
            background-color: rgba(70, 70, 70, 0.6);
            padding: 0.8rem;
            border-radius: 8px;
            border-left: 4px solid #FFA500;
            margin: 0.5rem 0;
            font-size: 0.9em;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 AI-Powered Blood Report Analyzer")
st.caption("🆓 Powered by Google Gemini (Free AI)")

# --- Load API Key from Secrets (Secure Method) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    ai_enabled = True
except:
    ai_enabled = False
    st.warning("⚠️ AI features disabled. Please configure GOOGLE_API_KEY in Streamlit secrets.")

# --- Extract Patient Info from PDF ---
def extract_patient_info(text):
    """Extract patient information from PDF text"""
    info = {
        "age": 0,
        "name": "",
        "id": ""
    }
    
    # Extract Age - common patterns
    age_patterns = [
        r"Age[:\s]+(\d{1,3})",  # Age: 45 or Age 45
        r"Age[:\s]+(\d{1,3})\s*(?:years|yrs|y)",  # Age: 45 years
        r"(\d{1,3})\s*(?:years old|yrs old|y/o)",  # 45 years old
        r"DOB.*?Age[:\s]+(\d{1,3})",  # DOB ... Age: 45
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            age = int(match.group(1))
            if 0 < age < 120:  # Sanity check
                info["age"] = age
                break
    
    # Extract Patient Name - common patterns
    name_patterns = [
        r"Patient Name[:\s]+([A-Z][a-zA-Z\s]+?)(?:\n|(?:Age|DOB|ID|MRN))",
        r"Name[:\s]+([A-Z][a-zA-Z\s]+?)(?:\n|(?:Age|DOB|ID|MRN))",
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info["name"] = match.group(1).strip()
            break
    
    # Extract Patient ID/MRN
    id_patterns = [
        r"(?:Patient ID|MRN|Medical Record)[:\s]+([A-Z0-9-]+)",
        r"ID[:\s]+([A-Z0-9-]+)",
    ]
    
    for pattern in id_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info["id"] = match.group(1).strip()
            break
    
    return info

# --- Sidebar for Patient Context ---
with st.sidebar:
    st.header("⚙️ Patient Context (Optional)")
    
    # Initialize patient info in session state
    if 'patient_info' not in st.session_state:
        st.session_state.patient_info = {"age": 0, "name": "", "id": ""}
    
    patient_age = st.number_input("Patient Age", min_value=0, max_value=120, value=st.session_state.patient_info["age"], help="Auto-extracted from PDF or enter manually")
    patient_conditions = st.text_area("Known Conditions", placeholder="e.g., Diabetes, Hypertension, CKD Stage 5", help="Enter any known medical conditions")
    current_medications = st.text_area("Current Medications", placeholder="e.g., Insulin, Lisinopril, EPO", help="List current medications")
    
    # Rate limit display
    st.markdown("---")
    st.header("📊 API Usage")
    remaining = rate_limiter.get_remaining_requests()
    st.metric("Requests Remaining", f"{remaining}/15")
    st.caption("Resets every minute")
    
    if ai_enabled:
        st.success("✅ AI Analysis Enabled")
    else:
        st.info("💡 Get free API key from: https://aistudio.google.com/app/apikey")

raw_text = ""
results = []

# --- 检查项目 ---
items_info = {
    "Creatinine": ("µmol/L", 44, 110),
    "Uric Acid":("µmol/L", 120, 420),
    "Urea": ("mmol/L", 3.0, 9.0),
    "Potassium": ("mmol/L", 3.5, 5.1),
    "Sodium": ("mmol/L", 135, 145),
    "Albumin": ("g/L", 35, 50),
    "Bilirubin": ("µmol/L", None, None),
    "Calcium": ("mmol/L", 2.10, 2.55),
    "Corrected Calcium": ("mmol/L", 2.10, 2.55),
    "Phosphate": ("mmol/L", 0.65, 1.45),
    "Alkaline Phosphatase": ("U/L", 40, 130),
    "AST": ("U/L", None, None),
    "ALT": ("U/L", None, None),
    "Haemoglobin": ("g/dL", 120, 150),
    "White Cell Count": ("µl", None, None),
    "Hypochromic cells": ("%", None, None),
    "Platelets": ("10^9/L", 150, 410),
    "Glucose": ("mmol/L", 3.9, 7.7),
    "Total Protein": ("g/L", None, None),
    "HbA1C": ("%", None, None),
    "Serum Iron": ("µmol/L", 9.0, 26.0),
    "Sr. UIBC": ("µmol/L", None, None),
    "Total Iron Binding Capacity": ("µmol/L", None, None),
    "Saturation": ("%", 13, 51),
    "Ferritin": ("µg/L", None, None),
    "Total Chol": ("mmol/L", None, None),
    "Triglyceride": ("mmol/L", None, None),
    "LDL-C L": ("mmol/L", None, None),
    "HDL-C": ("mmol/L", None, None),
    "Intact Parathyroid Hormone": ("pg/mL", 1.6, 6.9),
    "Lymphocytes": ("HSD/CU mm", 1.0, 4.0),
    "Urea - Post Dialysis": ("mmol/L", 3.0, 9.0),
    "GGT": ("U/L", None, None),
}

aliases = {
    "Urea": ["Blood Urea", "Urea (BUN)"],
    "Urea - Post Dialysis": ["Postdialysis Urea", "Post BUN"],
    "Sr. Creatinine": ["Creatinine", "Serum Creatinine"],
    "ALT": ["谷草转氨基酶", "ALT/SGPT (U/L)","A L T"],
    "AST": ["谷丙转氨基酶", "AST/SGOT (U/L)","A S T"],
}

reverse_alias = {}
for key, alist in aliases.items():
    for alias in alist:
        reverse_alias.setdefault(alias, []).append(key)

# --- 上传 PDF ---
uploaded_file = st.file_uploader("Upload a Lab Report PDF", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    raw_text = ""

    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text").strip()
            if text:
                st.info(f"✅ Page {i+1}: Text extracted.")
                raw_text += text.replace("\n", " ")
            else:
                st.warning(f"⚠️ Page {i+1}: No text detected (likely image-only PDF).")
        st.success(f"{doc.page_count} pages processed.")
    
    # Extract patient information from PDF
    patient_info = extract_patient_info(raw_text)
    st.session_state.patient_info = patient_info
    
    # Display extracted patient info
    if patient_info["age"] > 0 or patient_info["name"] or patient_info["id"]:
        with st.expander("👤 Auto-Extracted Patient Information", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                if patient_info["name"]:
                    st.metric("Patient Name", patient_info["name"])
            with col2:
                if patient_info["age"] > 0:
                    st.metric("Age", f"{patient_info['age']} years")
            with col3:
                if patient_info["id"]:
                    st.metric("Patient ID", patient_info["id"])

    with st.expander("📜 Raw Text from PDF"):
        st.text_area("Extracted Text Preview", raw_text[:3000])

# --- 分析数据 ---
if raw_text:
    for item, (unit, low, high) in items_info.items():
        patterns = [item] + reverse_alias.get(item, [])
        value_found = False
        for pattern in patterns:
            match = re.search(rf"{pattern}\D*([\d.]+)", raw_text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    mark = "*" if (low and value < low) or (high and value > high) else ""
                    ref = f"{low}-{high}" if low and high else "-"
                    results.append([item, f"{value}{mark}", ref])
                except:
                    results.append([item, "⚠️ Failed to parse", "-"])
                value_found = True
                break
        if not value_found:
            results.append([item, "Not found", "-"])

    df = pd.DataFrame(results, columns=["Test", "Value", "Reference Range"])
    st.subheader("🧪 Lab Result Analysis")
    st.dataframe(df)

# --- Serology Data Extraction ---
def interpret_result(text):
    """Interpret positive/negative keywords in text."""
    if any(word in text.lower() for word in ["not detected", "negative", "non reactive"]):
        return "Negative"
    elif any(word in text.lower() for word in ["detected", "positive", "reactive"]):
        return "Positive"
    else:
        return "Not done"

def extract_serology(text):
    """Extract serology test results from report text."""
    results = {}

    # HIV
    hiv = re.search(r"HIV.*?(Not Detected|Detected|Negative|Positive|Reactive|Non Reactive)", text, re.IGNORECASE)
    results["Anti HIV antibody"] = interpret_result(hiv.group(1)) if hiv else "Not done"

    # Hepatitis B surface antigen
    hbsag = re.search(r"Hepatitis B Surface antigen.*?(Not Detected|Detected|Negative|Positive)", text, re.IGNORECASE)
    results["Hep B antigen (HBsAg)"] = interpret_result(hbsag.group(1)) if hbsag else "Not done"

    # Hepatitis B surface antibody (HBsAb)
    hbsab = re.search(r"Hepatitis B Surface antibody.*?(\d+\.?\d*)\s*IU/L", text, re.IGNORECASE)
    results["Hep B antibody (HBsAb)"] = f"Positive ({hbsab.group(1)} IU/L)" if hbsab else "Not done"

    # Hepatitis C antibody
    hcv = re.search(r"Hepatitis C antibody.*?(Not Detected|Detected|Negative|Positive)", text, re.IGNORECASE)
    results["Anti HCV antibody"] = interpret_result(hcv.group(1)) if hcv else "Not done"

    results["Hep B Core antibody (HBcAb)"] = "Not done"

    return results

# --- 显示 Serology 结果 ---
sero_results = None
if raw_text:
    sero_results = extract_serology(raw_text)
    st.subheader("🧬 Serology Results")
    st.table(pd.DataFrame(list(sero_results.items()), columns=["Test", "Result"]))

# --- KT/V & URR 计算 ---
results_dict = {row[0]: row[1] for row in results}

dialysis_time = st.number_input("Dialysis Duration (hours)", min_value=1.0, max_value=8.0, value=4.0, step=0.5)
uf_volume = st.number_input("Ultrafiltration Volume (L)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)
post_weight = st.number_input("Post-dialysis Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)

kt_v = None
URR = None

try:
    urea = float(results_dict["Urea"].replace("*", ""))
    post_urea = float(results_dict["Urea - Post Dialysis"].replace("*", ""))

    R = post_urea / urea
    URR = round((1 - R) * 100, 2)
    kt_v = -math.log(R - 0.008 * dialysis_time) + ((4 - 3.5 * R) * (uf_volume / post_weight))
    kt_v = round(kt_v, 2)

    st.subheader("⏳ KT/V & URR Results")
    st.table(pd.DataFrame({
        "Metric": ["URR (%)", "KT/V"],
        "Value": [URR, kt_v]
    }))
except Exception as e:
    st.warning(f"⚠️ Cannot calculate KT/V & URR: {e}")

# --- AI Analysis Section ---
if raw_text and results and ai_enabled:
    st.markdown("---")
    st.subheader("🤖 AI-Powered Clinical Insights")
    
    # Show rate limit status
    remaining = rate_limiter.get_remaining_requests()
    if remaining > 0:
        st.markdown(f'<div class="rate-limit-info">📊 AI requests remaining: <strong>{remaining}/15</strong> (resets every minute)</div>', unsafe_allow_html=True)
    else:
        wait_time = int(rate_limiter.get_wait_time())
        st.markdown(f'<div class="warning-box">⏱️ Rate limit reached. Please wait <strong>{wait_time}</strong> seconds before next request.</div>', unsafe_allow_html=True)
    
    # Disable button if rate limit exceeded
    button_disabled = not rate_limiter.can_make_request()
    
    if st.button("🔍 Generate AI Analysis & Recommendations", type="primary", disabled=button_disabled):
        if rate_limiter.can_make_request():
            with st.spinner("🧠 AI is analyzing the blood test results..."):
                try:
                    # Record this request
                    rate_limiter.add_request()
                    
                    # Prepare data for AI
                    lab_results_text = df.to_string()
                    serology_text = pd.DataFrame(list(sero_results.items()), columns=["Test", "Result"]).to_string() if sero_results else "No serology data"
                    
                    kt_v_text = f"KT/V: {kt_v}, URR: {URR}%" if kt_v and URR else "KT/V and URR not calculated"
                    
                    # Build context
                    context = f"""
Patient Context:
- Age: {patient_age if patient_age > 0 else 'Not provided'}
- Known Conditions: {patient_conditions if patient_conditions else 'None specified'}
- Current Medications: {current_medications if current_medications else 'None specified'}

Lab Results:
{lab_results_text}

Serology Results:
{serology_text}

Dialysis Adequacy:
{kt_v_text}
- Dialysis Time: {dialysis_time} hours
- Ultrafiltration: {uf_volume} L
- Post-dialysis Weight: {post_weight} kg
"""

                    prompt = f"""You are an experienced nephrology and dialysis nurse assistant. Analyze the following blood test results and provide clinical insights.

{context}

Please provide:

1. **Critical Findings**: Identify any values that are significantly abnormal and require immediate attention (marked with *)

2. **Key Observations**: Summarize the overall picture - what do these results tell us about the patient's condition?

3. **Dialysis Adequacy Assessment**: Evaluate the KT/V and URR values (KT/V target: ≥1.2, URR target: ≥65%)

4. **Clinical Recommendations**: 
   - Monitoring suggestions
   - Potential medication adjustments to consider
   - Dietary recommendations
   - Follow-up testing if needed

5. **Nursing Considerations**: Practical points for dialysis unit nurses managing this patient

Please be specific, practical, and prioritize patient safety. Use clear language suitable for healthcare professionals."""

                    # Call Gemini API (using correct model name)
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                    
                    ai_response = response.text
                    
                    # Display AI insights
                    st.markdown(f'<div class="ai-suggestion">{ai_response}</div>', unsafe_allow_html=True)
                    
                    # Update remaining requests display
                    new_remaining = rate_limiter.get_remaining_requests()
                    st.info(f"✅ Analysis complete. {new_remaining} requests remaining this minute.")
                    
                    # Add disclaimer
                    st.warning("⚠️ **Disclaimer**: This AI analysis is for informational purposes only and should not replace professional clinical judgment. Always consult with a physician for medical decisions.")
                    
                except Exception as e:
                    st.error(f"❌ Error generating AI analysis: {str(e)}")
                    st.info("Please check the API configuration or try again later.")
        else:
            wait_time = int(rate_limiter.get_wait_time())
            st.error(f"⏱️ Rate limit exceeded. Please wait {wait_time} seconds before making another request.")

elif raw_text and results and not ai_enabled:
    st.info("💡 AI analysis is not configured. Get your free API key from: https://aistudio.google.com/app/apikey")
