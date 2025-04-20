
# 🌍 Chubb Climate Risk & Insurance Gen-AI Agent

This project was built for the **Chubb Empower Her InsureTech Hackathon 2025**. It is a Gen-AI-powered Streamlit app designed to help insurers monitor real-time news related to climate risk, policies, and insurance impact.

## 🚀 Features

- 🔍 **Real-Time News Scraping**: Pulls live articles from climate and insurance-focused RSS feeds.
- 🧠 **AI Summarization**: Uses Google Gemini Pro to summarize articles into short, structured insights.
- 🏷️ **Domain Classification**: Tags insights under categories like `Climate Risk`, `Policies`, etc.
- 📥 **Export Reports**: Generate and download a PDF summary for use in reports and presentations.
- 💡 **Fallback Feeds**: In case selected feed fails, it tries alternative sources like NASA or Google News.

## 🛠️ How to Run the App

### 1. Clone the repository

```bash
git clone https://github.com/your-username/chubb-climate-genai-agent.git
cd chubb-climate-genai-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API Key

Create a `.env` file or set the environment variable:

```bash
export GEMINI_API_KEY=your_google_gemini_api_key
```

> You can get a Gemini API key at: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 4. Run the Streamlit app

```bash
streamlit run app.py
```

## 📊 Evaluation Metrics

This app satisfies the hackathon evaluation criteria:

| Metric                    | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| ✅ Real-Time Scraping     | Fetches live RSS-based news from multiple climate/insurance sources         |
| ✅ AI Insight Extraction  | Uses Gen-AI for summarization and classification                            |
| ✅ Structured Output      | Provides filterable, categorized report snippets                            |
| ✅ Export Functionality   | PDF export built-in                                                         |
| ✅ Ethics & Transparency  | No user data, respects ethical AI guidelines, uses public data only         |

## 🧾 Sample Output

You can export summaries as PDF directly from the app interface.

## 👩‍💻 Built For

This project was built as part of the [Chubb Empower Her InsureTech Hackathon 2025](https://machinehack.com/ideathons/chubb-empower-her-insure-tech-hackathon-2025/overview).

---

Made with 💙 for climate resilience and innovation in insurance.
