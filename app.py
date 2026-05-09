import streamlit as st
import fitz  
import pandas as pd
import re
import math
import google.generativeai as genai
from datetime import datetime
from collections import deque

# --- Rate Limiter Class ---
class RateLimiter:
    def __init__(self, max_requests=15, time_window=60):
        if 'request_times' not in st.session_state:
            st.session_state.request_times = deque()
        self.max_requests = max_requests
        self.time_window = time_window
    
    def can_make_request(self):
        now = datetime.now()
        while st.session_state.request_times and \
              (now - st.session_state.request_times[0]).total_seconds() > self.time_window:
            st.session_state.request_times.popleft()
        return len(st.session_state.request_times) < self.max_requests
    
    def add_request(self):
        st.session_state.request_times.append(datetime.now())
    
    def get_wait_time(self):
        if len(st.session_state.request_times) < self.max_requests:
            return 0
        oldest_request = st.session_state.request_times[0]
        elapsed = (datetime.now() - oldest_request).total_seconds()
        return max(0, self.time_window - elapsed)
    
    def get_remaining_requests(self):
        now = datetime.now()
        while st.session_state.request_times and \
              (now - st.session_state.request_times[0]).total_seconds() > self.time_window:
            st.session_state.request_times.popleft()
        return self.max_requests - len(st.session_state.request_times)

# Initialize rate limiter
rate_limiter = RateLimiter(max_requests=15, time_window=60)

# --- UI 样式 ---
st.markdown("""
    <style>
        .stApp {
            background-image: url("[github.com](https://github.com/USAGI7878/Blood-report_kt-v/raw/main/background%20ver%202.png)");
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
        .stButton > button {
            background-color: #555;
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

# --- Load API Key ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    ai_enabled = True
except Exception as e:
    ai_enabled = False
    st.warning(f"⚠️ AI features disabled. Error: {e}")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Patient Context (Optional)")
    if 'patient_info' not in st.session_state:
        st.session_state.patient_info = {"age": 0, "name": "", "id": ""}
    
    patient_age = st.number_input("Patient Age", min_value=0, max_value=120, value=st.session_state.patient_info["age"])
    patient_conditions = st.text_area("Known Conditions")
    current_medications = st.text_area("Current Medications")
    
    st.markdown("---")
    st.header("📊 API Usage")
    remaining = rate_limiter.get_remaining_requests()
    st.metric("Requests Remaining", f"{remaining}/15")
    st.caption("Resets every minute")
    if ai_enabled:
        st.success("✅ AI Analysis Enabled")
    else:
        st.info("💡 Get free API key from: [aistudio.google.com](https://aistudio.google.com/app/apikey)")

raw_text = ""
results = []

# --- Dialysis parameters ---
st.subheader("📋 请先填写透析参数")
col1, col2, col3 = st.columns(3)
with col1:
    dialysis_time = st.number_input("Dialysis Duration (hours)", min_value=1.0, max_value=8.0, value=4.0, step=0.5)
with col2:
    uf_volume = st.number_input("Ultrafiltration Volume (L)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)
with col3:
    post_weight = st.number_input("Post-dialysis Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
st.markdown("---")

# --- 上传 PDF（只留一处）---
st.subheader("📄 上传血液报告")
uploaded_file = st.file_uploader("Upload a Lab Report PDF", type="pdf")

# --- Helper function ---
def extract_patient_info(text):
    info = {"age": 0, "name": "", "id": ""}
    age_match = re.search(r"Age[:\s]+(\d{1,3})", text, re.IGNORECASE)
    if age_match:
        info["age"] = int(age_match.group(1))
    name_match = re.search(r"Patient Name[:\s]+([A-Z][a-zA-Z\s]+)", text)
    if name_match:
        info["name"] = name_match.group(1).strip()
    id_match = re.search(r"(?:Patient ID|MRN)[:\s]+([A-Z0-9-]+)", text)
    if id_match:
        info["id"] = id_match.group(1).strip()
    return info

# --- Process PDF ---
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        raw_text = " ".join([page.get_text("text").strip().replace("\n", " ") for page in doc])
    st.success(f"✅ PDF processed successfully ({doc.page_count} page{'s' if doc.page_count>1 else ''})")
    st.session_state.patient_info = extract_patient_info(raw_text)

    with st.expander("👤 Auto-Extracted Patient Information", expanded=True):
        st.write(st.session_state.patient_info)

# --- 后续的化验提取、AI分析等按原逻辑继续 ---
# 为简洁性省略，逻辑不变（所有后续的 results、AI 分析部分保持原样）
