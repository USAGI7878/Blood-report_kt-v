# Batch Medical Lab Report Analyzer (Multiple PDFs)
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import math

st.title("🧪 Medical Lab Report Analyzer (PDF)")

# 初始化变量
raw_text = ""
results = []

# 上传多个文件
uploaded_files = st.file_uploader("Upload Lab Reports (PDF)", type="pdf", accept_multiple_files=True)

# 单个病人的报告分析
if uploaded_files:
    for uploaded_file in uploaded_files:
        raw_text = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                raw_text += page.get_text().replace("\n", " ")
        
        st.success(f"File '{uploaded_file.name}' loaded. Analyzing...")

        # 分析 PDF 文本
        current_results = []
        for item, (unit, low, high) in items_info.items():
            patterns = [item] + reverse_alias.get(item, [])
            value_found = False
            for pattern in patterns:
                match = re.search(rf"{pattern}.*?([\d.]+)", raw_text, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        mark = "*" if (low and value < low) or (high and value > high) else ""
                        ref = f"{low}-{high}" if low and high else "-"
                        current_results.append([item, f"{value}{mark}", ref])
                    except:
                        current_results.append([item, "⚠️ Failed to parse", "-"])
                    value_found = True
                    break
            if not value_found:
                current_results.append([item, "Not found", "-"])

        # Display Results for the Current Patient
        df = pd.DataFrame(current_results, columns=["Test", "Value", "Reference Range"])
        st.subheader(f"🧪 Lab Result Analysis for {uploaded_file.name}")
        st.dataframe(df)

        # Serology results (optional)
        if raw_text:
            sero = extract_serology(raw_text)
            st.subheader(f"🧬 Serology Results for {uploaded_file.name}")
            st.table(pd.DataFrame(list(sero.items()), columns=["Test", "Result"]))

# 如果只上传一个病人的报告文件
else:
    st.info("Please upload a lab report file to begin analysis.")

items_info = {
    "Urea": ("mmol/L", 3.0, 9.0),
    "Urea - Post Dialysis": ("mmol/L", 3.0, 9.0),
    "Creatinine": ("µmol/L", 44, 110),
    "Potassium": ("mmol/L", 3.5, 5.1),
    "Sodium": ("mmol/L", 135, 145),
    "Albumin": ("g/L", 35, 50),
    "Bilirubin": ("µmol/L", None, None),
    "Calcium": ("mmol/L", 2.10, 2.55),
    "Phosphate": ("mmol/L", 0.65, 1.45),
    "Alkaline Phosphatase": ("U/L", 40, 130),
    "ALT": ("U/L", None, None),
    "AST": ("U/L", None, None),
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
    "GGT": ("U/L", None, None),
}

aliases = {
    "Urea": ["Blood Urea", "Urea (BUN)"],
    "Urea - Post Dialysis": ["Postdialysis Urea", "Post BUN"],
    "Sr. Creatinine": ["Creatinine", "Serum Creatinine"],
}

reverse_alias = {}
for key, alist in aliases.items():
    for alias in alist:
        reverse_alias.setdefault(alias, []).append(key)

# Serology helpers
def interpret_result(text):
    if "not detected" in text.lower() or "negative" in text.lower() or "non reactive" in text.lower():
        return "Negative"
    elif "detected" in text.lower() or "positive" in text.lower() or "reactive" in text.lower():
        return "Positive"
    else:
        return "Not done"

def extract_serology(text):
    results = {}
    hiv = re.search(r"HIV.*?(Not Detected|Detected|Negative|Positive|Reactive|Non Reactive)", text, re.IGNORECASE)
    results["Anti HIV antibody"] = interpret_result(hiv.group(1)) if hiv else "Not done"
    hbsag = re.search(r"Hepatitis B Surface antigen.*?(Not Detected|Detected|Negative|Positive)", text, re.IGNORECASE)
    results["Hep B antigen (HBsAg)"] = interpret_result(hbsag.group(1)) if hbsag else "Not done"
    hbsab = re.search(r"Hepatitis B Surface antibody.*?(\d+\.?\d*)\s*IU/L", text, re.IGNORECASE)
    results["Hep B antibody (HBsAb)"] = f"Positive ({hbsab.group(1)} IU/L)" if hbsab else "Not done"
    hcv = re.search(r"Hepatitis C antibody.*?(Not Detected|Detected|Negative|Positive)", text, re.IGNORECASE)
    results["Anti HCV antibody"] = interpret_result(hcv.group(1)) if hcv else "Not done"
    results["Hep B Core antibody (HBcAb)"] = "Not done"
    return results

# File uploader for multiple PDFs
uploaded_files = st.file_uploader("Upload multiple PDF lab reports", type="pdf", accept_multiple_files=True)

all_data = []

if uploaded_files:
    for file in uploaded_files:
        raw_text = ""
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                raw_text += page.get_text().replace("\n", " ")

        result_row = {"Patient": file.name}

        for item, (unit, low, high) in items_info.items():
            patterns = [item] + reverse_alias.get(item, [])
            found = False
            for pattern in patterns:
                match = re.search(rf"{pattern}.*?([\d.]+)", raw_text, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        if (low and value < low) or (high and value > high):
                            result_row[item] = f"❗ {value}"
                        else:
                            result_row[item] = value
                    except:
                        result_row[item] = "⚠️ Parse error"
                    found = True
                    break
            if not found:
                result_row[item] = "-"

        # Add serology
        sero = extract_serology(raw_text)
        result_row.update(sero)

        all_data.append(result_row)

    df = pd.DataFrame(all_data)
    st.subheader("📊 Batch Result Table")
    st.dataframe(df)

    # Download button
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button("📥 Download as Excel", data=buffer.getvalue(), file_name="lab_results.xlsx")


