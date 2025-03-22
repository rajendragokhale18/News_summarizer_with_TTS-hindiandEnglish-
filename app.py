import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from news_scraper import get_news
from news_sentiment import comparative_analysis, text_to_speech
import os

# Set page configuration
st.set_page_config(page_title="News Sentiment & Data Analysis", layout="wide")

# ✅ Ensure session state variables are initialized (Fix UI Reset Issue)
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "English"

if "analysis_done" not in st.session_state:
    st.session_state["analysis_done"] = False  # Track if analysis has been performed

if "speech_ready" not in st.session_state:
    st.session_state["speech_ready"] = False  # Track if speech is generated

if "speech_file" not in st.session_state:
    st.session_state["speech_file"] = None  # Store speech file path

# App Title
st.markdown("<h1 style='text-align: center; color: #FFA500;'>📰 AI-Powered News Sentiment & Company Data Analysis</h1>", unsafe_allow_html=True)

# User input for company name
company_name = st.text_input("🔍 Enter a Company Name (e.g., Tesla, Apple):", value="Tesla")

if st.button("Analyze News"):
    st.session_state["analysis_done"] = True  # ✅ Set flag when analysis is performed
    st.session_state["company_name"] = company_name  # Store company name persistently
    st.session_state["speech_ready"] = False  # Reset speech flag

# ✅ Show results only if analysis has been performed
if st.session_state["analysis_done"]:
    st.write(f"📡 Fetching and analyzing news for: **{st.session_state['company_name']}**")

    # Fetch news articles
    news_data = get_news(st.session_state["company_name"])

    if "error" in news_data:
        st.error(news_data["error"])
    else:
        st.subheader("📢 Latest News & Sentiment Analysis")

        # Display news articles
        for article in news_data:
            st.write(f"🔹 **{article['title']}**")
            st.write(f"🔗 [Read More]({article['link']})")
            st.write(f"🧭 Sentiment: **{article['sentiment']}**\n")

        # Perform comparative analysis (Limit to 2 comparisons)
        sentiment_report = comparative_analysis(news_data)
        st.subheader("📊 Comparative Sentiment Analysis Report")

        if "Coverage Differences" in sentiment_report and len(sentiment_report["Coverage Differences"]) > 0:
            st.write("📌 **Key Comparisons:**")
            for comparison in sentiment_report["Coverage Differences"][:2]:  # ✅ Show only 2 comparisons
                st.write(f"- **{comparison['Comparison']}**")
                st.write(f"  🔹 **Impact:** {comparison['Impact']}")

        # Add Company Data Analysis Section
        st.subheader("📈 Company Financial Data")

        try:
            stock_symbol = yf.Ticker(st.session_state["company_name"])
            stock_info = stock_symbol.info

            st.write(f"**Company Name:** {stock_info.get('longName', 'N/A')}")
            st.write(f"**Stock Price:** ${stock_info.get('regularMarketPrice', 'N/A')}")
            st.write(f"**Market Cap:** ${stock_info.get('marketCap', 'N/A')}")
            st.write(f"**52-Week High:** ${stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
            st.write(f"**52-Week Low:** ${stock_info.get('fiftyTwoWeekLow', 'N/A')}")
            st.write(f"**Revenue:** ${stock_info.get('totalRevenue', 'N/A')}")

            # 📊 Stock Price Trend Chart
            st.subheader("📊 Stock Price Trend")
            stock_data = stock_symbol.history(period="6mo")
            if not stock_data.empty:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(stock_data.index, stock_data["Close"], label="Stock Price", color="blue")
                ax.set_xlabel("Date")
                ax.set_ylabel("Stock Price ($)")
                ax.legend()
                st.pyplot(fig)

        except Exception as e:
            st.error(f"⚠️ Error fetching financial data: {str(e)}")

        # 📊 Sentiment Distribution Chart
        st.subheader("📊 Sentiment Distribution")
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for article in news_data:
            sentiment_counts[article["sentiment"]] += 1

        sentiment_df = pd.DataFrame(list(sentiment_counts.items()), columns=["Sentiment", "Count"])
        st.bar_chart(sentiment_df.set_index("Sentiment"))

        # ✅ Language selection is asked **only when downloading**
        st.subheader("🎙️ Speech Generation")

        selected_language = st.radio("Choose language for speech:", ["English", "Hindi"], index=0 if st.session_state["selected_language"] == "English" else 1)
        st.session_state["selected_language"] = selected_language  # ✅ Store in session_state

        lang_code = "en" if selected_language == "English" else "hi"

        # ✅ Generate speech only when button is clicked
        if st.button("🎧 Generate Speech Summary"):
            speech_file = text_to_speech(str(sentiment_report), lang=lang_code)
            if speech_file and os.path.exists(speech_file):
                st.session_state["speech_file"] = speech_file  # Store speech file path
                st.session_state["speech_ready"] = True  # ✅ Set flag so download button appears

        # ✅ Show Download Button only after speech is generated
        if st.session_state["speech_ready"] and st.session_state["speech_file"]:
            speech_file = st.session_state["speech_file"]

            st.subheader("🔊 Listen to Summary")
            st.audio(speech_file, format="audio/mp3")

            with open(speech_file, "rb") as file:
                st.download_button("⬇️ Download Audio", file, file_name=f"{st.session_state['company_name']}_sentiment_summary.mp3")
