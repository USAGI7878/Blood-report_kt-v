import streamlit as st
import fitz  
import pandas as pd
import re
import math

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
    </style>
""", unsafe_allow_html=True)

st.title("🧪 Medical Lab Report Analyzer (PDF)")

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

# --- KT/V & URR 计算 ---
results_dict = {row[0]: row[1] for row in results}

dialysis_time = st.number_input("Dialysis Duration (hours)", min_value=1.0, max_value=8.0, value=4.0, step=0.5)
uf_volume = st.number_input("Ultrafiltration Volume (L)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)
post_weight = st.number_input("Post-dialysis Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)

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
    st.warning(f"Waiting for Urea & Post Urea values: {e}")
