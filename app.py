import streamlit as st
import fitz  
import pandas as pd
import re
import math
#import easyocr

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
        .stChatMessage {
            background-color: #333;
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

# identify key and value 

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
    "Urea - Post Dialysis": ("mmol/L", 3.0, 9.0),
    "GGT": ("U/L", None, None),
}

aliases = {
    "Urea": ["Blood Urea", "Urea (BUN)"],
    "Urea - Post Dialysis": ["Postdialysis Urea", "Post BUN"],
    "Sr. Creatinine": ["Creatinine", "Serum Creatinine"],
    "ALT": ["谷草转氨基酶", "ALT/SGPT (U/L)"],
    "AST": ["谷丙转氨基酶", "AST/SGOT (U/L)"],

}

# create key

reverse_alias = {}
for key, alist in aliases.items():
    for alias in alist:
        reverse_alias.setdefault(alias, []).append(key)

# upload file 

uploaded_file = st.file_uploader("Upload a Lab Report PDF", type="pdf")
if uploaded_file is not None:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
    raw_text += page.get_text("text").replace("\n", " ")
    st.success(f"{doc.page_count} pages loaded.")

    with st.expander("📜 Raw Text from PDF"):
        st.text(raw_text)

# analyze PDF data

if raw_text:
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

results_dict = {row[0]: row[1] for row in results}
# Serology data extraction

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
    results["Hep B Core antibody (HBcAb)"] = "Not done"  
    return results

#show result 
if raw_text:
    sero = extract_serology(raw_text)
    st.subheader("🧬 Serology Results")
    st.table(pd.DataFrame(list(sero.items()), columns=["Test", "Result"]))



# user input data 
dialysis_time = st.number_input("Dialysis Duration (hours)", min_value=1.0, max_value=8.0, value=4.0, step=0.5)
uf_volume = st.number_input("Ultrafiltration Volume (L)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)
post_weight = st.number_input("Post-dialysis Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)

try:
    urea = float(results_dict["Urea"].replace("*", ""))
    post_urea = float(results_dict["Urea - Post Dialysis"].replace("*", ""))

    R = post_urea / urea
    URR = round((1 - R) * 100, 2)
    try:
        kt_v = -math.log(R - 0.008 * dialysis_time) + ((4 - 3.5 * R) * (uf_volume / post_weight))
        kt_v = round(kt_v, 2)
    except:
        kt_v = "⚠️ Calculation error"

    st.subheader("⏳ KT/V & URR Results")
    st.table(pd.DataFrame({
        "Metric": ["URR (%)", "KT/V"],
        "Value": [URR, kt_v]
    }))
except Exception as e:
    st.warning(f"Waiting for input on Urea and Post: {e}")
# --- Bot Section ---
import streamlit as st
st.subheader("🤖 Ask the BOT Assistant")

user_question = st.chat_input("Ask me about KT/V, lab test meanings, or how to use this tool...")
if user_question:
    with st.chat_message("user"):
        st.write(user_question)

    response = ""

    if "kt/v" in user_question.lower():
        response = "KT/V is ... > 1.2"
    elif "urr" in user_question.lower():
        response = "URR ... > 65%"
    elif "how to use" in user_question.lower() or "upload" in user_question.lower():
        response = "After uploading the PDF ..."
    elif "hb" in user_question.lower() or "haemoglobin" in user_question.lower():
        response = "Haemoglobin ... 10-12 g/dL"
    elif "phosphate" in user_question.lower():
        response = "High phosphate ... below 1.45 mmol/L"
    else:
        response = "Currently, I can only answer questions related to KT/V, URR..."

    with st.chat_message("assistant"):
        st.write(response)

#mini game 
import random

st.title("🐾 Cat Interaction Game ")
st.title("🐾 Relax time ! ")


# original mood 
if "affection" not in st.session_state:
    st.session_state.affection = 0
    st.session_state.cat_mood = "neutral"
    st.session_state.cat_coming = False  # 
    st.session_state.cat_coming = False  #

# cat resposes 
cat_responses = {
    "head": ["😺 Purr... loves head pats!", "😸 Happy kitty~"],
    "chin": ["😽 Leans in for more...", "😻 Favorite spot!"],
    "tail": ["🙀 Hisses! Don't touch the tail!", "😾 Annoyed..."],
    "butt": ["😼 Wiggles... suspicious but ok", "😹 Embarrassed but accepts it"],
}

part = st.radio("Where do you want to pet the cat?", ["head", "chin", "tail", "butt"], horizontal=True)

# press button to start the game 
if st.button("Pet the cat 🐱"):
    response = random.choice(cat_responses[part])
    st.write(f"🧤 You pet the cat's {part}.\n\n{response}")

    # changes 
    if part in ["head", "chin"]:
        st.session_state.affection += 1
        st.session_state.cat_mood = "happy"
    elif part == "butt":
        st.session_state.affection += random.choice([0, 1])
        st.session_state.cat_mood = "confused"
    else:
        st.session_state.affection -= 1
        st.session_state.cat_mood = "grumpy"

    # hit the target
    if st.session_state.affection >= 10 and not st.session_state.cat_coming:
        st.session_state.cat_coming = True
        st.write("🎉 The cat is coming to you! You’ve earned its trust! 🐱💖")


#show affection level
st.metric("🐾 Affection Level", st.session_state.affection)


# cat emotion with pictures 
cat_images = {
    "happy": "https://i.imgflip.com/t1qbu.jpg?a484752",  
    "neutral": "https://www.meowbox.com/cdn/shop/articles/Screen_Shot_2024-03-15_at_10.53.41_AM.png?v=1710525250", 
    "grumpy": "https://s.rfi.fr/media/display/48adfe80-10b6-11ea-b699-005056a99247/w:1280/p:1x1/grumpy_cat.jpg",  
    "happy": "https://i.imgflip.com/t1qbu.jpg?a484752",  
    "neutral": "https://www.meowbox.com/cdn/shop/articles/Screen_Shot_2024-03-15_at_10.53.41_AM.png?v=1710525250",  
    "grumpy": "https://s.rfi.fr/media/display/48adfe80-10b6-11ea-b699-005056a99247/w:1280/p:1x1/grumpy_cat.jpg",  
    "confused": "https://i.imgflip.com/64ngqc.png"  
}

st.image(cat_images[st.session_state.cat_mood], width=300, caption="Your cat's current mood 🐾")


# to show max affection level
if st.session_state.cat_coming:
    st.image("https://i.pinimg.com/474x/41/c8/85/41c885962c25860bf8bf0ae6ebf8255c.jpg", width=300, caption="Your cat is coming to you! 🐾💖")






