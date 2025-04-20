import streamlit as st
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import tempfile
import feedparser
import re
import os
import google.generativeai as genai

# -------------------- GEMINI SETUP -------------------------- #
# IMPORTANT: Replace 'YOUR_API_KEY' with your Gemini API key.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_api_key")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# -------------------- SUMMARIZATION -------------------------- #
#@st.cache_resource(show_spinner=False)
def summarize_and_tag(text: str) -> dict:
    try:
        # Clean and limit text more aggressively
        cleaned_text = re.sub(r'[^\w\s.,-]', '', text[:2000])  # Remove special chars and limit to 2000 chars
        prompt = f"Summarize this news article in 3-5 sentences:\n\n{cleaned_text}"
        response = model.generate_content(prompt)
        summary = response.text.strip()
        if not summary:
            summary = "The article discusses climate and policy topics but details could not be summarized."
    except Exception as e:
        st.error(f"Gemini API error: {str(e)}")
        summary = "[Error generating summary]"

    domain = "Climate Risk" if "climate" in text.lower() else "Policies"  # Use original text for domain detection
    return {"domain": domain, "summary": summary}

# -------------------- REAL-TIME NEWS (RSS) ------------------ #
def fetch_rss_articles(feed_urls: List[str]) -> List[str]:
    article_texts = []
    for feed_url in feed_urls:
        try:
            st.write(f"🔄 Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                st.warning(f"⚠️ No entries found in feed: {feed_url}")
                continue
                
            st.write(f"📰 Found {len(feed.entries)} entries in feed")
            
            for i, entry in enumerate(feed.entries[:3]):  # Limit to top 3 per feed
                url = entry.link
                st.write(f"🔗 Scraping article {i+1}: {url}")
                content = scrape_simple_text(url)
                if content and len(content) > 100:  # Ensure we have meaningful content
                    st.write(f"✅ Successfully scraped {len(content)} characters")
                    article_texts.append(content)
                else:
                    st.warning(f"⚠️ Failed to scrape article or content too short: {url}")
        except Exception as e:
            st.error(f"❌ Error processing feed {feed_url}: {str(e)}")
    
    return article_texts

# -------------------- SCRAPING ------------------------------- #
def scrape_simple_text(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # Try extracting meaningful content with fallbacks
        content_areas = []
        
        # Try common article containers
        for selector in ['article', 'main', '.content', '.article-body', '.story-body', '.post-content']:
            elements = soup.select(selector)
            if elements:
                content_areas.extend(elements)
        
        # If nothing found, fallback to body
        if not content_areas:
            content_areas = [soup.find('body')]
            
        # Extract text from found content areas
        all_text = []
        for area in content_areas:
            if area:
                paragraphs = area.find_all('p')
                if paragraphs:
                    all_text.extend([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        text = " ".join(all_text)
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with single newline
        
        return text.strip()
    except Exception as e:
        st.write(f"Scraping error: {str(e)}")
        return ""

# ---------------------- EXPORT PDF -------------------------- #
def export_report_pdf(summaries: List[Dict]) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for item in summaries:
        pdf.multi_cell(0, 10, f"[{item['domain']}] - {item['summary']}\n")
    temp_path = tempfile.mktemp(suffix=".pdf")
    pdf.output(temp_path)
    return temp_path

# ---------------------- STREAMLIT UI ------------------------ #
st.set_page_config(page_title="Chubb Climate Risk AI Agent", layout="wide")
st.title("🌍 Chubb Climate Risk & Insurance Gen-AI Agent")

# Sidebar Info
with st.sidebar:
    st.header("📄 About this App")
    st.markdown("""
    This Streamlit app demonstrates a Gen-AI powered agent that:
    - Scrapes real climate/insurance-related news
    - Summarizes & categorizes using **Google Gemini Pro**
    - Exports structured reports
    - Uses **real-time RSS feeds** for live news
    """)
    st.markdown("---")
    st.header("🧠 Ethics")
    st.markdown("""
    - Uses public, credible sources
    - No personal info processed
    - Results may require human verification
    """)

# Initialize session state
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "articles" not in st.session_state:
    st.session_state.articles = []
if "fallback_attempted" not in st.session_state:
    st.session_state.fallback_attempted = False

# Step 1 - Select Source
st.subheader("🔎 Step 1 - Choose a News Feed")
sources = {
    "Reuters Climate": "http://feeds.reuters.com/reuters/environment",
    "Insurance Journal": "https://www.insurancejournal.com/feed/",
    "Climate Change News": "https://www.climatechangenews.com/feed/",
    "EcoWatch": "https://www.ecowatch.com/feed"
}
selected_label = st.selectbox("Choose a news feed:", list(sources.keys()))
selected_feed_url = sources[selected_label]

if st.button("🚀 Run Agent"):
    st.session_state.fallback_attempted = False  # Reset fallback flag
    with st.spinner("Scraping real-time news and summarizing with Gemini..."):
        st.session_state.articles = fetch_rss_articles([selected_feed_url])
        st.write(f"✅ Fetched {len(st.session_state.articles)} articles")
        st.session_state.summaries = [summarize_and_tag(text) for text in st.session_state.articles if text.strip()]
    st.success("Done! See the structured summaries below.")
    if not st.session_state.summaries:
        st.warning("No summaries were generated. The articles may have failed to scrape or are not readable.")

# Add this BEFORE your "Show summaries" code block
if not st.session_state.summaries and not st.session_state.fallback_attempted:
    st.warning("Unable to fetch articles from the selected feed.")
    if st.button("Try alternative feeds"):
        st.session_state.fallback_attempted = True
        with st.spinner("Trying fallback news sources..."):
            fallback_feeds = ["https://news.google.com/rss/search?q=climate+change", 
                             "https://climate.nasa.gov/feed/"]
            st.session_state.articles = fetch_rss_articles(fallback_feeds)
            st.write(f"✅ Fetched {len(st.session_state.articles)} articles from fallback feeds")
            st.session_state.summaries = [summarize_and_tag(text) for text in st.session_state.articles if text.strip()]
        if st.session_state.summaries:
            st.success("Successfully retrieved articles from alternative sources!")
        else:
            st.error("Still unable to retrieve articles. Please try again later or check your internet connection.")

# Show summaries if they exist
if st.session_state.summaries:
    st.subheader("📑 Summarized Insights")
    domains = list(set(item['domain'] for item in st.session_state.summaries))
    selected_domain = st.selectbox("Filter by domain:", ["All"] + domains)

    for item in st.session_state.summaries:
        if selected_domain == "All" or item['domain'] == selected_domain:
            st.markdown(f"**[{item['domain']}]** - {item['summary']}")

    pdf_path = export_report_pdf(st.session_state.summaries)
    with open(pdf_path, "rb") as file:
        st.download_button("📥 Export as PDF", file, file_name="Chubb_Climate_Summary.pdf", mime="application/pdf")
else:
    st.info("Click the 'Run Agent' button to generate summaries.")