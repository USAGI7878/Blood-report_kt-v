# 🩸 AI-Powered Blood Report Analyzer

> A comprehensive web application designed for dialysis unit nurses to analyze blood test reports with AI-powered clinical insights.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blood-reportkt-v-6ekbavp3osoe8ajbit9ysh.streamlit.app/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

This tool revolutionizes how dialysis units handle blood test analysis by combining automated PDF extraction, intelligent data parsing, and AI-powered clinical recommendations. Built by a dialysis nurse with software development aspirations, it bridges the gap between clinical needs and technology.

### 🎯 Key Features

- **📄 Automated PDF Processing** - Upload blood test PDFs and extract text/results instantly using PyMuPDF (`fitz`).
- **🤖 Interactive AI Clinical Insights** - Get intelligent initial analysis and ask follow-up questions via a conversational chat interface powered by AI.
- **👤 Patient Information Extraction** - Automatically detect age, name, and patient ID directly from the report text.
- **🧪 Comprehensive Lab Analysis** - Track 30+ blood markers with built-in reference ranges and multi-language alias support (English & Chinese).
- **🧬 Serology Testing** - Automated HIV, Hepatitis B/C result interpretation and quantification tracking (e.g., HBsAb IU/L).
- **📊 Dialysis Adequacy** - Real-time **KT/V** and **URR** automated calculations based on pre- and post-dialysis data.
- **🔒 Session-Based Rate Limiting** - Built-in secure protection (15 requests/minute) with a rolling 60-second window and dynamic countdown UI.
- **💾 Secure & Private** - Zero data retention; all processing happens dynamically in-memory.

---

## 🚀 Live Demo

👉 **[Try the App Now](https://blood-reportkt-v-6ekbavp3osoe8ajbit9ysh.streamlit.app/)**

---

## 📸 Screenshots & Interface

### 1. Dialysis Parameters & PDF Upload
Clean dark-themed interface with intuitive inputs for dialysis time, ultrafiltration volume, and post-weight, paired with a robust PDF processing engine.

### 2. Lab Result Dataframe & Serology
Clear table rendering highlighting abnormal indicators (`*`) alongside parsed serology results (Negative / Positive / Not done).

### 3. Interactive AI Assistant
A dedicated conversational interface allowing nurses to ask follow-up questions seamlessly after receiving the initial clinical recommendation profile.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive responsive dark-theme web interface |
| **PDF Processing** | PyMuPDF (fitz) | High-speed structured text extraction from PDFs |
| **Data Analysis** | Pandas | Lab result alignment, formatting, and rendering |
| **AI Engine** | Google Gemini API | Dual-layered model routing for clinical insights and interactive chat |
| **Rate Limiting** | Custom Python Class (`deque`) | Session-safe API usage quota protection |
| **Deployment** | Streamlit Cloud | Live application hosting |

---

## 📋 What It Analyzes

### Blood Chemistry & Hematology (30+ markers)
- **Renal Function**: Creatinine, Urea, Uric Acid, Urea - Post Dialysis
- **Electrolytes**: Sodium, Potassium, Calcium, Corrected Calcium, Phosphate
- **Liver Function & Enzymes**: Albumin, Total Protein, Bilirubin, Alkaline Phosphatase, AST, ALT, GGT *(Supports Chinese/English text mapping)*
- **Hematology**: Haemoglobin, White Cell Count, Lymphocytes, Platelets, Hypochromic

#### Get Free API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`) and paste it into `.streamlit/secrets.toml`

---

## 📖 How to Use

1. **Set Parameters**: Define Dialysis Duration, Ultrafiltration Volume, and Post-dialysis Weight at the top.
2. **Upload PDF**: Upload an electronically generated PDF lab report (scanned image PDFs are not supported yet).
3. **Verify Extractions**: Review the auto-detected Patient Info, Lab Results table (abnormal markers are highlighted with `*`), and Serology data.
4. **Context Injection (Optional)**: Input known conditions or current medications in the sidebar to enrich the AI's understanding.
5. **Generate Insights**: Click **🔍 Generate AI Analysis & Recommendations** to review the clinical breakdown.
6. **Follow-up Chat**: Use the conversational chat box below the results to ask specific questions (e.g., *"Why is the potassium level high?"* or *"What dietary tips apply here?"*).

---

## 🔐 Security & Privacy

### Data Protection
- ✅ **No Data Storage** - All processing happens dynamically in-memory; files and text are destroyed when the session ends.
- ✅ **No Trace Logs** - Patient data is never saved to a disk or external log collector.
- ✅ **Secure API** - All API configurations leverage Streamlit's native backend `secrets.toml` architecture.
- ✅ **Session-Based Limit** - 15 requests per minute per session to prevent API quota abuse while keeping the UI responsive.

---

## 🎓 Clinical Disclaimer

⚠️ **IMPORTANT MEDICAL DISCLAIMER**

This tool is designed as a workflow assistant for **healthcare professionals (specifically dialysis unit nurses)**, and does not replace professional clinical judgment.
- AI analysis is for **informational purposes only**.
- Always cross-verify critical values with official laboratory documents and attending nephrologists.
- Do not make standalone adjustments to prescriptions or dialysis routines without licensed medical supervision.

---

## 🗺️ Roadmap

### Current Features (v1.1) ✅
- [x] In-memory PDF parsing and auto-extraction.
- [x] Pre/Post-dialysis biochemical tracking & Chinese alias mapping.
- [x] Dynamic URR and Daugirdas KT/V calculations.
- [x] Multi-model backup support (`gemini-1.5-flash`, `gemini-1.5-pro`).
- [x] Conversational follow-up chat loops.
- [x] Rolling 60s window rate-limiter logic.

### Planned Features (v2.0) 🚧
- [ ] OCR engine integration for image-only/scanned PDFs.
- [ ] Trend line visualizations over multiple consecutive monthly reports.
- [ ] Report exporter to Excel (`.xlsx`) or polished PDF formats.
- [ ] Broader localization support (Malay, Chinese native UI routing).

---

## 👨‍⚕️ About the Author

Created by **a dialysis nurse in Malaysia** passionate about:
- 🏥 Improving patient care through technology
- 💻 Learning software development
- 🌉 Bridging healthcare and tech
- 🚀 Building practical clinical tools

This project combines frontline dialysis experience with modern AI technology to solve real healthcare workflow challenges. 

If this tool helps your clinical practice, please consider giving this repository a ⭐ on GitHub! 🌍💙

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
