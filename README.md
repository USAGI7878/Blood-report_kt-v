# 🩸 Blood Report KT/V Analyzer

A simple, lightweight web app to help dialysis unit nurses and clinicians **analyze KT/V and serology blood test reports** more efficiently.

🚑 Designed with real clinical scenarios in mind — created by a nurse with software aspirations.

## 🌟 Why I built this

In dialysis units, we often need to manually calculate and track KT/V, serology results, and urea reduction. This tool:
- Reduces time spent on manual work
- Organizes lab results in a clear, editable table
- Aims to be used directly by healthcare workers

## 🛠️ Tech Stack

- **Streamlit**: For quick interactive UI
- **Python (Pandas)**: Data manipulation
- **OpenCV / PDF extraction (optional future)**
- **Basic spreadsheet logic** (editable KT/V fields)

## ✨ Features

- Upload lab report data (CSV or manually input)
- Auto-fills most fields except KT/V
- Editable fields for manual input
- Auto-calculates URR and formats data neatly
- Built-in table styling for readability
- Option to export result table (future)

## 📷 Preview

![screenshot](./preview.png) 

## 🧪 Try It Now

👉 [Click here to open the demo](https://usagi7878-blood-report-kt-v.streamlit.app/)

## 🧰 How to Run Locally

```bash
git clone https://github.com/USAGI7878/Blood-report_kt-v.git
cd Blood-report_kt-v
pip install -r requirements.txt
streamlit run app.py
🗓️ Next Steps
Add PDF upload and parsing

Add charts for KT/V trends over time

Export to Excel with formatting

Multilingual support (English + 中文)

🙋 About Me
I'm a dialysis nurse in Malaysia with a strong interest in software development and AI.
I built this project to help bridge the gap between healthcare needs and tech solutions.
