import streamlit as st
import fitz  
import pandas as pd
import re
import math
import json
from anthropic import Anthropic

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
    </style>
""", unsafe_allow_html=True)

st.title("🧪 AI-Powered Blood Report Analyzer")

# --- Load API Key from Secrets (Secure Method) ---
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    ai_enabled = True
except:
    ai_enabled = False
    st.warning("⚠️ AI features disabled. Please configure ANTHROPIC_API_KEY in Streamlit secrets.")

# --- Sidebar for Patient Context ---
with st.sidebar:
    st.header("⚙️ Patient Context (Optional)")
    patient_age = st.number_input("Patient Age", min_value=0, max_value=120, value=0, help="Helps AI provide age-appropriate recommendations")
    patient_conditions = st.text_area("Known Conditions", placeholder="e.g., Diabetes, Hypertension, CKD Stage 5", help="Enter any known medical conditions")
    current_medications = st.text_area("Current Medications", placeholder="e.g., Insulin, Lisinopril, EPO", help="List current medications")
    
    if ai_enabled:
        st.success("✅ AI Analysis Enabled")
    else:
        st.info("💡 AI analysis requires API key configuration")

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
    
    if st.button("🔍 Generate AI Analysis & Recommendations", type="primary"):
        with st.spinner("🧠 AI is analyzing the blood test results..."):
            try:
                # Initialize Anthropic client
                client = Anthropic(api_key=api_key)
                
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

                # Call Claude API
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                ai_response = message.content[0].text
                
                # Display AI insights
                st.markdown(f'<div class="ai-suggestion">{ai_response}</div>', unsafe_allow_html=True)
                
                # Add disclaimer
                st.warning("⚠️ **Disclaimer**: This AI analysis is for informational purposes only and should not replace professional clinical judgment. Always consult with a physician for medical decisions.")
                
            except Exception as e:
                st.error(f"❌ Error generating AI analysis: {str(e)}")
                st.info("Please check the API configuration.")

elif raw_text and results and not ai_enabled:
    st.info("💡 AI analysis is not configured. Please add ANTHROPIC_API_KEY to Streamlit secrets to enable this feature.")
