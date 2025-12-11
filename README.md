# 🩸 AI-Powered Blood Report Analyzer

> A comprehensive web application designed for dialysis unit nurses to analyze blood test reports with AI-powered clinical insights.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blood-reportkt-v-6ekbavp3osoe8ajbit9ysh.streamlit.app/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

This tool revolutionizes how dialysis units handle blood test analysis by combining automated PDF extraction, intelligent data parsing, and AI-powered clinical recommendations. Built by a dialysis nurse with software development aspirations, it bridges the gap between clinical needs and technology.

### 🎯 Key Features

- **📄 Automated PDF Processing** - Upload blood test PDFs and extract results instantly
- **🤖 AI Clinical Insights** - Get intelligent analysis powered by Google Gemini AI
- **👤 Patient Information Extraction** - Automatically detect age, name, and patient ID
- **🧪 Comprehensive Lab Analysis** - Track 30+ blood markers with reference ranges
- **🧬 Serology Testing** - Automated HIV, Hepatitis B/C result interpretation
- **📊 Dialysis Adequacy** - KT/V and URR calculation with clinical targets
- **🔒 Rate Limiting** - Built-in API protection (15 requests/minute)
- **💾 Secure & Private** - No data storage, all processing in-memory

---

## 🚀 Live Demo

👉 **[Try the App Now](https://blood-reportkt-v-6ekbavp3osoe8ajbit9ysh.streamlit.app/)**

---

## 📸 Screenshots

### Main Interface
Clean, professional interface with automatic PDF processing:
- Upload blood test reports
- View extracted lab results
- Auto-detected patient information
- AI-powered clinical recommendations

### AI Analysis
Comprehensive clinical insights including:
- Critical findings identification
- Dialysis adequacy assessment
- Clinical recommendations
- Nursing considerations

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **PDF Processing** | PyMuPDF (fitz) | Text extraction from PDFs |
| **Data Analysis** | Pandas | Lab result organization |
| **AI Engine** | Google Gemini API | Clinical insights generation |
| **Rate Limiting** | Custom Python class | API usage protection |
| **Deployment** | Streamlit Cloud | Free hosting |

---

## 📋 What It Analyzes

### Blood Chemistry (30+ markers)
- Renal function: Creatinine, Urea, Uric Acid
- Electrolytes: Sodium, Potassium, Calcium, Phosphate
- Liver function: ALT, AST, Bilirubin, Alkaline Phosphatase
- Hematology: Hemoglobin, WBC, Platelets
- Metabolic: Glucose, HbA1C, Cholesterol, Triglycerides
- Bone health: Parathyroid Hormone, Calcium, Phosphate
- Iron status: Serum Iron, Ferritin, TIBC, Saturation

### Serology Testing
- HIV antibody
- Hepatitis B (HBsAg, HBsAb, HBcAb)
- Hepatitis C antibody

### Dialysis Adequacy
- **KT/V** calculation (target ≥1.2)
- **URR** calculation (target ≥65%)
- Personalized recommendations

---

## 🎯 Use Cases

### For Dialysis Nurses
- ✅ Quick review of monthly blood work
- ✅ Identify critical values requiring immediate attention
- ✅ Track dialysis adequacy (KT/V, URR)
- ✅ Generate patient care recommendations
- ✅ Document serology status for infection control

### For Healthcare Facilities
- ✅ Standardize blood test review process
- ✅ Reduce time spent on manual calculations
- ✅ Improve consistency in patient assessment
- ✅ Support clinical decision-making
- ✅ Educational tool for new staff

### For Patients
- ✅ Better understand lab results
- ✅ Track health trends over time
- ✅ Prepare for doctor consultations

---

## 🏃 Quick Start

### Option 1: Use the Live App (Recommended)
Simply visit: **[blood-reportkt-v.streamlit.app](https://blood-reportkt-v-6ekbavp3osoe8ajbit9ysh.streamlit.app/)**

### Option 2: Run Locally

#### Prerequisites
- Python 3.12 or higher
- Google AI Studio API Key (free)

#### Installation

```bash
# Clone the repository
git clone https://github.com/USAGI7878/Blood-report_kt-v.git
cd Blood-report_kt-v

# Install dependencies
pip install -r requirements.txt

# Create secrets file
mkdir .streamlit
echo 'GOOGLE_API_KEY = "your-api-key-here"' > .streamlit/secrets.toml

# Run the app
streamlit run app.py
```

#### Get Free API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)
4. Add to `.streamlit/secrets.toml`

---

## 📖 How to Use

### Step 1: Upload Blood Test PDF
- Click "Browse files" or drag & drop
- Supported format: PDF with text (not image-only)
- The app automatically extracts all text

### Step 2: Review Extracted Data
- **Patient Information**: Age, name, ID auto-detected
- **Lab Results**: 30+ markers with reference ranges
- **Serology**: HIV, Hep B/C status
- **Abnormal Values**: Marked with `*` for easy identification

### Step 3: Enter Dialysis Data (Optional)
- Dialysis duration (hours)
- Ultrafiltration volume (L)
- Post-dialysis weight (kg)
- KT/V and URR calculated automatically

### Step 4: Add Patient Context (Optional)
In the sidebar:
- Patient age (if not auto-detected)
- Known conditions (e.g., Diabetes, Hypertension)
- Current medications (e.g., Insulin, EPO)

### Step 5: Generate AI Analysis
- Click "🔍 Generate AI Analysis & Recommendations"
- Wait 5-10 seconds for AI processing
- Review comprehensive clinical insights:
  - **Critical Findings**: Urgent issues
  - **Key Observations**: Overall health picture
  - **Dialysis Adequacy**: KT/V and URR assessment
  - **Clinical Recommendations**: Actionable suggestions
  - **Nursing Considerations**: Practical care tips

---

## 🔐 Security & Privacy

### Data Protection
- ✅ **No data storage** - All processing in-memory
- ✅ **No logs** - Patient data not saved to disk
- ✅ **Secure API** - Keys stored in Streamlit secrets
- ✅ **HIPAA considerations** - Suitable for healthcare use
- ✅ **Session-based** - Data cleared when you close the browser

### API Rate Limiting
- 15 requests per minute per session
- Prevents API quota abuse
- Fair usage across multiple users
- Automatic reset every 60 seconds

---

## 🎓 Clinical Disclaimer

⚠️ **IMPORTANT MEDICAL DISCLAIMER**

This tool is designed to **assist** healthcare professionals, not replace clinical judgment.

- AI analysis is for **informational purposes only**
- Always verify with licensed physicians
- Do not use as sole basis for medical decisions
- Emergency situations require immediate medical attention
- Not a substitute for professional medical advice

**Always consult with qualified healthcare providers for medical decisions.**

---

## 🗺️ Roadmap

### Current Features (v1.0) ✅
- [x] PDF upload and text extraction
- [x] Automated lab result parsing
- [x] Patient information extraction
- [x] AI-powered clinical analysis
- [x] KT/V and URR calculation
- [x] Serology interpretation
- [x] Rate limiting protection

### Planned Features (v2.0) 🚧
- [ ] Multi-language support (English, Chinese, Malay)
- [ ] Trend analysis across multiple reports
- [ ] Export results to PDF/Excel
- [ ] Historical data comparison
- [ ] Custom reference ranges
- [ ] Mobile app version
- [ ] OCR for image-only PDFs
- [ ] Medication interaction checker

### Long-term Vision (v3.0) 💡
- [ ] Integration with hospital EMR systems
- [ ] Machine learning for pattern detection
- [ ] Automated lab ordering suggestions
- [ ] Patient portal for result access
- [ ] Multi-facility support
- [ ] Advanced analytics dashboard

---

## 🤝 Contributing

Contributions are welcome! This project was created by a dialysis nurse learning software development.

### How to Contribute
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Areas Needing Help
- 🐛 Bug fixes and testing
- 📝 Documentation improvements
- 🌐 Translation to other languages
- 🎨 UI/UX enhancements
- 🧪 Additional lab test patterns
- 📊 Data visualization features

---

## 📝 Development Notes

### Project Structure
```
Blood-report_kt-v/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml      # API keys (local only)
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── .devcontainer/        # Dev container config
```

### Key Dependencies
- `streamlit>=1.50.0` - Web framework
- `PyMuPDF>=1.26.5` - PDF processing
- `pandas>=2.3.3` - Data manipulation
- `google-generativeai>=0.3.0` - AI integration

### Rate Limiter Design
```python
class RateLimiter:
    - Tracks requests per session
    - Rolling 60-second window
    - Prevents API abuse
    - User-friendly countdown
```

---

## 💰 Cost Analysis

### Free Tier (Current)
- **Google Gemini API**: 1,500 requests/day (FREE)
- **Streamlit Cloud**: Unlimited hosting (FREE)
- **Total Cost**: $0/month for typical usage

### Estimated Usage
- Small clinic (10 patients/day): ~10 API calls/day
- Medium facility (50 patients/day): ~50 API calls/day  
- Large unit (200 patients/day): ~200 API calls/day

**All within free tier limits!** 🎉

---

## 🐛 Troubleshooting

### Common Issues

**Q: "AI features disabled" message**  
A: Check your API key in Streamlit secrets. Get a new key from https://aistudio.google.com/app/apikey

**Q: "No compatible models found"**  
A: You're using the wrong API key. Use Google AI Studio (not Google Cloud Console).

**Q: PDF not extracting text**  
A: Your PDF might be image-only. Try using the debug section to check extracted text.

**Q: Age/patient info not detected**  
A: The app looks for common patterns. You can manually enter the information in the sidebar.

**Q: Rate limit reached**  
A: Wait 60 seconds. The limit resets every minute (15 requests/min).

---

## 📞 Support & Contact

### Get Help
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/USAGI7878/Blood-report_kt-v/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/USAGI7878/Blood-report_kt-v/discussions)
- 📧 **Direct Contact**: Open an issue on GitHub

### Useful Links
- **Live App**: https://blood-reportkt-v-6ekbavp3osoe8ajbit9ysh.streamlit.app/
- **GitHub Repo**: https://github.com/USAGI7878/Blood-report_kt-v
- **Google AI Studio**: https://aistudio.google.com/
- **Streamlit Docs**: https://docs.streamlit.io/

---

## 👨‍⚕️ About the Author

Created by **a dialysis nurse in Malaysia** passionate about:
- 🏥 Improving patient care through technology
- 💻 Learning software development
- 🌉 Bridging healthcare and tech
- 🚀 Building practical clinical tools

This project combines years of frontline dialysis experience with modern AI technology to solve real healthcare challenges.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Free for personal and commercial use
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute copies
- ✅ Private use
- ❌ No liability or warranty
```

---

## 🙏 Acknowledgments

- **Google Gemini AI** - For providing free AI capabilities
- **Streamlit** - For the amazing web framework
- **PyMuPDF** - For reliable PDF processing
- **Dialysis Community** - For inspiration and feedback
- **Open Source Contributors** - For dependencies and tools

---

## ⭐ Show Your Support

If this tool helps your clinical practice:
- ⭐ **Star** this repository
- 🐛 **Report** bugs to help improve it
- 💡 **Suggest** features you'd like to see
- 📢 **Share** with colleagues who might benefit

**Together, we can improve dialysis care worldwide!** 🌍💙

---

<div align="center">

**Made with ❤️ by a Nurse who Codes**

[Report Bug](https://github.com/USAGI7878/Blood-report_kt-v/issues) · [Request Feature](https://github.com/USAGI7878/Blood-report_kt-v/issues) · [View Demo](https://blood-reportkt-v-6ekbavp3osoe8ajbit9ysh.streamlit.app/)

</div>
