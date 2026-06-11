🩸 AI-Powered Blood Report Analyzer
A comprehensive web application designed for dialysis unit nurses to analyze blood test reports with AI-powered clinical insights.

🌟 Overview
This tool revolutionizes how dialysis units handle blood test analysis by combining automated PDF extraction, intelligent data parsing, and AI-powered clinical recommendations. Built by a dialysis nurse with software development aspirations, it bridges the gap between clinical needs and technology.

🎯 Key Features
📄 Automated PDF Processing - Upload blood test PDFs and extract results instantly using PyMuPDF (fitz).

🤖 Interactive AI Clinical Insights - Get intelligent analysis and ask follow-up questions via conversational chat powered by Google Gemini AI.

👤 Patient Information Extraction - Automatically detect patient name, age, and ID directly from the report text.

🧪 Comprehensive Lab Analysis - Track 30+ blood markers with built-in reference ranges and multi-language alias support (English & Chinese).

🧬 Serology Testing - Automated HIV, Hepatitis B/C result interpretation and quantification tracking (e.g., HBsAb IU/L).

📊 Dialysis Adequacy - Real-time KT/V and URR automated calculations based on pre- and post-dialysis data.

🔒 Session-Based Rate Limiting - Built-in secure protection (15 requests/minute) with dynamic countdown UI.

💾 Secure & Private - Zero data retention; all file processing happens dynamically in-memory.

🚀 Live Demo
👉 Try the App Now

📸 Screenshots
1. Dialysis Parameters & PDF Upload
Clean dark-themed interface with intuitive inputs for dialysis time, ultrafiltration volume, and post-weight, paired with a robust PDF processing engine.

2. Lab Result Dataframe & Serology
Clear table rendering highlighting abnormal indicators (*) alongside parsed serology results (Negative / Positive / Not done).

3. Interactive AI Assistant
A dedicated conversational interface allowing nurses to ask follow-up questions seamlessly after receiving the initial clinical recommendation profile.

🛠️ Technology Stack
Component	Technology	Purpose
Frontend	Streamlit	Interactive responsive dark-theme web interface
PDF Processing	PyMuPDF (fitz)	High-speed structured text extraction from PDFs
Data Analysis	Pandas	Lab result alignment, formatting, and rendering
AI Engine	Google Gemini API	Dual-layered model routing for clinical insights and interactive chat
Rate Limiting	Custom Python Class (deque)	Session-safe API usage quota protection
Deployment	Streamlit Cloud	Live application hosting
📋 What It Analyzes
Blood Chemistry & Hematology (30+ markers)
Renal Function: Creatinine, Urea, Uric Acid, Urea - Post Dialysis

Electrolytes: Sodium, Potassium, Calcium, Corrected Calcium, Phosphate

Liver Function & Enzymes: Albumin, Total Protein, Bilirubin, Alkaline Phosphatase, AST, ALT, GGT (Supports Chinese/English text routing)

Hematology: Haemoglobin, White Cell Count, Lymphocytes, Platelets, Hypochromic cells

Metabolic / Metabolic Status: Glucose, HbA1C, Total Chol, Triglyceride, LDL-C, HDL-C

Bone Health: Intact Parathyroid Hormone (iPTH), Calcium, Phosphate

Iron Profile: Serum Iron, Sr. UIBC, Total Iron Binding Capacity, Saturation, Ferritin

Serology Testing
Anti-HIV antibody

Hepatitis B panel (HBsAg, HBsAb with titers, HBcAb)

Anti-HCV antibody

Dialysis Adequacy Assessment
URR Calculation: URR=(1− 
Pre Urea
Post Urea
​
 )×100%

KT/V Calculation: Dynamic Daugirdas formula processing incorporating ultrafiltration volume and post-dialysis weight target assessments.

🏃 Quick Start
Option 1: Use the Live App (Recommended)
Simply visit: blood-reportkt-v.streamlit.app

Option 2: Run Locally
Prerequisites
Python 3.12 or higher

Google AI Studio API Key (Get a free key)

Installation
Bash
# Clone the repository
git clone https://github.com/USAGI7878/Blood-report_kt-v.git
cd Blood-report_kt-v

# Install dependencies
pip install -r requirements.txt

# Create secrets directory and setup local key
mkdir .streamlit
echo 'GOOGLE_API_KEY = "your-api-key-here"' > .streamlit/secrets.toml

# Run the app
streamlit run app.py
📖 How to Use
Set Parameters: Define Dialysis Duration, Ultrafiltration Volume, and Post-dialysis Weight.

Upload PDF: Upload an electronically generated PDF lab report.

Verify Extractions: Review the auto-detected Patient Info, Lab Results table (abnormal markers are highlighted with *), and Serology data.

Context Injection (Optional): Input known conditions or current medications in the sidebar to enrich the AI's understanding.

Generate Insights: Click 🔍 Generate AI Analysis & Recommendations to review the clinical breakdown.

Follow-up Chat: Use the conversational chat box below the results to ask specific questions (e.g., "Why is the potassium level high?" or "What dietary tips apply here?").

🔐 Security & Privacy
🚫 No Permanent Storage: Patient files and text records are processed entirely in-memory and destroyed when the session ends.

🚫 No Trace Logs: Patient records are never persisted to a disk or external log collector.

🔐 Secure Tokens: All API configurations leverage Streamlit's native backend secrets.toml architecture.

🎓 Clinical Disclaimer
⚠️ IMPORTANT MEDICAL DISCLAIMER

This tool is designed as a workflow assistant for healthcare professionals (specifically dialysis nurses), and does not replace professional clinical judgment.

AI analysis is purely informational.

Always cross-verify critical values with official laboratory documents and attending nephrologists.

Do not make standalone adjustments to prescriptions or dialysis routines without licensed supervision.

🗺️ Roadmap
Current Features (v1.1) ✅
[x] In-memory PDF parsing and auto extraction.

[x] Pre/Post-dialysis biochemical tracking.

[x] Dynamic URR and Daugirdas KT/V calculations.

[x] Multi-model backup support (gemini-1.5-flash, gemini-1.5-pro).

[x] Conversational follow-up chat loops.

[x] Rolling 60s window rate-limiter logic.

Planned Features (v2.0) 🚧
[ ] OCR engine integration for image-only/scanned PDFs.

[ ] Trend line visualizations over multiple consecutive monthly reports.

[ ] Report exporter to Excel (.xlsx) or polished PDF formats.

[ ] Broader localization support (Malay, Chinese native UI routing).

👨‍⚕️ About the Author
Created by a frontline Dialysis Nurse based in Malaysia on a mission to merge nursing expertise with software engineering.

If this tool streamlined your monthly shift workflows, please consider giving this project a ⭐ on GitHub!
