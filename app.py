import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
import math

st.set_page_config(page_title="Blood Report Analyzer", layout="wide")
st.title("📄 Automated Blood Report Analyzer")

uploaded_file = st.file_uploader("Upload PDF file", type="pdf")

# Initialize variables
raw_text = ""
file_bytes = None

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    if file_bytes:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            st.success(f"Successfully read {doc.page_count} pages from PDF")
            for page in doc:
                raw_text += page.get_text()
    else:
        st.error("Uploaded file is empty. Please upload a valid PDF.")
else:
    st.info("Please upload a PDF file.")

# Manual KT/V input
with st.expander("📊 Manually Enter KT/V & URR Parameters"):
    pre_bun = st.number_input("Pre-dialysis BUN (mmol/L)", value=19.7)
    post_bun = st.number_input("Post-dialysis BUN (mmol/L)", value=4.0)
    dialysis_time = st.number_input("Dialysis Time (hours)", value=4.0)
    uf_volume = st.number_input("Ultrafiltration Volume (L)", value=1.7)
    post_weight = st.number_input("Post-dialysis Weight (kg)", value=53.65)

# Lab test reference values
items_info = {
    "Creatinine": ("µmol/L", 53, 97),
    "Uric Acid": ("µmol/L", 120, 420),
    "Urea": ("mmol/L", 2.5, 6.4),
    "Post Urea": ("mmol/L", 1.7, 8.5),
    "Potassium": ("mmol/L", 3.5, 5.2),
    "Sodium": ("mmol/L", 136, 145),
    "Albumin": ("g/L", 38, 50),
    "Bilirubin": ("µmol/L", 1.71, 20.5),
    "Calcium": ("mmol/L", 2.1, 2.6),
    "Corrected Calcium": ("mmol/L", 2.1, 2.5),
    "Phosphate": ("mmol/L", 1.0, 1.5),
    "Alkaline Phosphatase": ("U/L", 36, 110),
    "ALT": ("U/L", 8, 54),
    "AST": ("U/L", 16, 40),
    "Haemoglobin": ("g/dL", 11.5, 18.0),
    "White Cell Count": ("x10⁹/L", 4.0, 10.0),
    "Platelets": ("10⁹/L", 150, 400),
    "RBC": ("x10¹²/L", 4.2, 5.8),
    "MCV": ("fL", 80, 100),
    "MCH": ("pg", 27, 32),
    "MCHC": ("g/dL", 32, 36),
    "Neutrophils": ("%", 40, 75),
    "Lymphocytes": ("%", 20, 45),
    "Monocytes": ("%", 2, 8),
    "Eosinophils": ("%", 1, 6),
    "Basophils": ("%", 0, 1),
    "Serum Iron": ("µmol/L", 9, 30),
    "Total Iron Binding Capacity": ("µmol/L", 50, 88),
    "Saturation": ("%", 10, 50),
    "Ferritin": ("µg/L", 15, 150),
    "Total Chol": ("mmol/L", None, 5.2),
    "Triglyceride": ("mmol/L", None, 2.3),
    "LDL-C": ("mmol/L", None, 3.4),
    "HDL-C": ("mmol/L", 0.9, None),
    "Intact Parathyroid Hormone": ("pmol/L", 1.6, 6.9),
    "Glucose": ("mmol/L", 3.9, 7.7),
    "HbA1c": ("%", 4.0, 6.0),
    "hs-CRP": ("mg/L", 0.0, 3.0),
    "Vitamin D": ("ng/mL", 20, 50)
}

# Alias mapping
alias_map = {
    "Cr": "Creatinine",
    "Uric": "Uric Acid",
    "BUN": "Urea",
    "Post BUN": "Post Urea",
    "Na": "Sodium",
    "K": "Potassium",
    "Alb": "Albumin",
    "Bili": "Bilirubin",
    "Ca": "Calcium",
    "Corrected Ca": "Corrected Calcium",
    "P": "Phosphate",
    "ALP": "Alkaline Phosphatase",
    "ALT(SGPT)": "ALT",
    "AST(SGOT)": "AST",
    "HGB": "Haemoglobin",
    "WBC": "White Cell Count",
    "PLT": "Platelets",
    "RBC Count": "RBC",
    "Fe": "Serum Iron",
    "TIBC": "Total Iron Binding Capacity",
    "PTH": "Intact Parathyroid Hormone",
    "TG": "Triglyceride",
    "Total Cholesterol": "Total Chol",
    "LDL": "LDL-C",
    "HDL": "HDL-C",
    "CRP": "hs-CRP",
    "Vit D": "Vitamin D",
    "HbA1C": "HbA1c"
}

# Reverse alias lookup
reverse_alias = {}
for k, v in alias_map.items():
    reverse_alias.setdefault(v, []).append(k)

# Extract results from text
results = []
if raw_text:
    for item, (unit, low, high) in items_info.items():
        patterns = [item] + reverse_alias.get(item, [])
        value_found = False
        for pattern in patterns:
            match = re.search(rf"{pattern}.*?([\d.]+)", raw_text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    ref = f"{low} - {high}" if low is not None and high is not None else "-"
                    mark = "*" if (low is not None and value < low) or (high is not None and value > high) else ""
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

# KT/V and URR calculation
if pre_bun > 0 and post_bun > 0:
    R = post_bun / pre_bun
    URR = round((1 - R) * 100, 2)
    try:
        kt_v = -math.log(R - 0.008 * dialysis_time) + ((4 - 3.5 * R) * (uf_volume / post_weight))
        kt_v = round(kt_v, 2)
    except:
        kt_v = "⚠️ Calculation error"

    st.subheader("⏳ KT/V & URR Results")
    ktv_data = {
        "Metric": ["URR (%)", "KT/V"],
        "Value": [URR, kt_v]
    }
    st.table(pd.DataFrame(ktv_data))
