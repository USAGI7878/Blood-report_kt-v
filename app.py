import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import math
st.markdown("""
    <style>
        .stApp {
            background-image: url("https://github.com/USAGI7878/Blood-report_kt-v/raw/main/background%20ver%202.png");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .block-container {
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 15px;
            padding: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 Medical Lab Report Analyzer (PDF)")

# 初始化变量
raw_text = ""
results = []

# 初始化项目信息和别名
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

# 构建反向别名映射
reverse_alias = {}
for key, alist in aliases.items():
    for alias in alist:
        reverse_alias.setdefault(alias, []).append(key)

# 上传文件并解析
uploaded_file = st.file_uploader("Upload a Lab Report PDF", type="pdf")
if uploaded_file is not None:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            raw_text += page.get_text().replace("\n", " ")
        st.success(f"{doc.page_count} pages loaded.")

    with st.expander("📜 Raw Text from PDF"):
        st.text(raw_text)

# 分析 PDF 文本
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
# Serology 提取函数
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

    results["Hep B Core antibody (HBcAb)"] = "Not done"  # 预留项目
    return results

# 显示 Serology 结果
if raw_text:
    sero = extract_serology(raw_text)
    st.subheader("🧬 Serology Results")
    st.table(pd.DataFrame(list(sero.items()), columns=["Test", "Result"]))


# 用户输入参数
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
# --- AI Bot Section ---
st.subheader("🤖 Ask the AI Assistant")

user_question = st.chat_input("Ask me about KT/V, lab test meanings, or how to use this tool...")
if user_question:
    with st.chat_message("user"):
        st.write(user_question)

    # 这里我们用简单规则生成答案，你也可以之后整合更强大的模型
    response = ""

    if "kt/v" in user_question.lower():
        response = "KT/V 是透析充分性指标，建议维持 KT/V > 1.2，表示透析效果良好。"
    elif "urr" in user_question.lower():
        response = "URR（尿素减少率）计算尿素清除率，通常 URR > 65% 被认为是足够的透析。"
    elif "how to use" in user_question.lower() or "upload" in user_question.lower():
        response = "上传 PDF 后，系统会自动提取血液检查与血清学结果，并计算 KT/V。"
    elif "hb" in user_question.lower() or "haemoglobin" in user_question.lower():
        response = "Haemoglobin 是血红蛋白指标，反映贫血情况，透析病人建议维持在 10-12 g/dL。"
    elif "phosphate" in user_question.lower():
        response = "磷过高会导致骨病，建议控制在 1.45 mmol/L 以下，可通过饮食与磷结合剂控制。"
    else:
        response = "目前我只能回答与 KT/V、URR、基本血检和系统操作有关的问题喔！"

    with st.chat_message("assistant"):
        st.write(response)
import streamlit as st
import random

st.title("🐾 Cat Interaction Game - 撸猫日常")

# 初始化状态
if "affection" not in st.session_state:
    st.session_state.affection = 0
    st.session_state.cat_mood = "neutral"
    st.session_state.cat_coming = False  # 新增的状态：猫咪是否主动过来

# 猫咪回应设定
cat_responses = {
    "head": ["😺 Purr... loves head pats!", "😸 Happy kitty~"],
    "chin": ["😽 Leans in for more...", "😻 Favorite spot!"],
    "tail": ["🙀 Hisses! Don't touch the tail!", "😾 Annoyed..."],
    "butt": ["😼 Wiggles... suspicious but ok", "😹 Embarrassed but accepts it"],
}

# 选择摸哪里
part = st.radio("Where do you want to pet the cat?", ["head", "chin", "tail", "butt"], horizontal=True)

# 点按钮开始摸猫
if st.button("Pet the cat 🐱"):
    response = random.choice(cat_responses[part])
    st.write(f"🧤 You pet the cat's {part}.\n\n{response}")
    
    # 改变亲密度与情绪
    if part in ["head", "chin"]:
        st.session_state.affection += 1
        st.session_state.cat_mood = "happy"
    elif part == "butt":
        st.session_state.affection += random.choice([0, 1])
        st.session_state.cat_mood = "confused"
    else:
        st.session_state.affection -= 1
        st.session_state.cat_mood = "grumpy"

    # 判断亲密值是否达到 10
    if st.session_state.affection >= 10 and not st.session_state.cat_coming:
        st.session_state.cat_coming = True
        st.write("🎉 The cat is coming to you! You’ve earned its trust! 🐱💖")

# 显示亲密值
st.metric("🐾 Affection Level", st.session_state.affection)

# 猫咪情绪表情
cat_images = {
    "happy": "https://i.imgflip.com/t1qbu.jpg?a484752",  # 用实际的 URL 替换
    "neutral": "https://www.meowbox.com/cdn/shop/articles/Screen_Shot_2024-03-15_at_10.53.41_AM.png?v=1710525250",  # 用实际的 URL 替换
    "grumpy": "https://s.rfi.fr/media/display/48adfe80-10b6-11ea-b699-005056a99247/w:1280/p:1x1/grumpy_cat.jpg",  # 用实际的 URL 替换
    "confused": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fmakerworld.com%2Fen%2Fmodels%2F921094-confused-cat-meme-cover-of-a1-a1mini-extruder&psig=AOvVaw3nlTarJCdIooX0UGKNezU4&ust=1746541033453000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCLD3ucLCjI0DFQAAAAAdAAAAABAE"  # 用实际的 URL 替换
}

st.image(cat_images[st.session_state.cat_mood], width=300, caption="Your cat's current mood 🐾")

# 显示猫咪图片（根据情绪）
cat_images = {
    "happy": "https://i.imgflip.com/t1qbu.jpg?a484752",  # 用实际的 URL 替换
    "neutral": "https://www.meowbox.com/cdn/shop/articles/Screen_Shot_2024-03-15_at_10.53.41_AM.png?v=1710525250",  # 用实际的 URL 替换
    "grumpy": "https://s.rfi.fr/media/display/48adfe80-10b6-11ea-b699-005056a99247/w:1280/p:1x1/grumpy_cat.jpg",  # 用实际的 URL 替换
    "confused": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fmakerworld.com%2Fen%2Fmodels%2F921094-confused-cat-meme-cover-of-a1-a1mini-extruder&psig=AOvVaw3nlTarJCdIooX0UGKNezU4&ust=1746541033453000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCLD3ucLCjI0DFQAAAAAdAAAAABAE"  # 用实际的 URL 替换
}
}
st.image(cat_images[st.session_state.cat_mood], width=300, caption="Your cat's current mood 🐾")

# 如果亲密值达到 10，显示猫咪主动过来的图
if st.session_state.cat_coming:
    st.image("https://i.pinimg.com/474x/41/c8/85/41c885962c25860bf8bf0ae6ebf8255c.jpg", width=300, caption="Your cat is coming to you! 🐾💖")


