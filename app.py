import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from news_scraper import get_news
from news_sentiment import comparative_analysis, text_to_speech
from yahoo_fin import stock_info
import os

# ✅ Set page configuration
st.set_page_config(page_title="News & Stock Sentiment Analysis", layout="wide")

# ✅ UI Title
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>📊 AI-Powered News & Stock Sentiment Analysis</h1>", unsafe_allow_html=True)

# ✅ User input for company name
company_name = st.text_input("🔍 Enter a Company Name (e.g., Tesla, Apple):", value="Tesla")

if st.button("Analyze News"):
    st.session_state["analysis_done"] = True
    st.session_state["company_name"] = company_name

# ✅ Function to get stock ticker from company name
def get_stock_ticker(company_name):
    try:
        ticker = stock_info.get_quote_table(company_name, dict_result=False).iloc[0]["Symbol"]
        return ticker
    except Exception:
        return None

# ✅ Show results only if analysis has been performed
if st.session_state.get("analysis_done"):
    st.write(f"📡 Fetching and analyzing news for: **{st.session_state['company_name']}**")

    # ✅ Fetch news articles
    news_data = get_news(st.session_state["company_name"])

    if "error" in news_data:
        st.error(news_data["error"])
    else:
        st.subheader("📢 Latest News & Sentiment Analysis")
        for article in news_data:
            st.write(f"🔹 **{article['title']}**")
            st.write(f"🔗 [Read More]({article['link']})")
            st.write(f"🧭 Sentiment: **{article['sentiment']}**\n")

        # ✅ Perform comparative analysis
        sentiment_report = comparative_analysis(news_data)
        st.subheader("📊 Comparative Sentiment Analysis Report")

        if "Coverage Differences" in sentiment_report:
            st.write("📌 **Key Comparisons:**")
            for comparison in sentiment_report["Coverage Differences"][:2]:
                st.write(f"- **{comparison['Comparison']}**")
                st.write(f"  🔹 **Impact:** {comparison['Impact']}")

        # ✅ Audio Download & Playback (Restored!)
        st.subheader("🎙️ Generate Speech")
        lang_option = st.radio("Choose language:", ["English", "Hindi"])
        lang_code = "en" if lang_option == "English" else "hi"

        if st.button("Generate & Download Speech"):
            speech_file = text_to_speech(str(sentiment_report), lang=lang_code)
            if os.path.exists(speech_file):
                st.audio(speech_file, format="audio/mp3")  # ✅ Audio Player is now visible
                st.download_button("⬇ Download Speech", open(speech_file, "rb"), file_name=speech_file)

        # ✅ Auto-Detect Stock Ticker
        stock_ticker = get_stock_ticker(st.session_state["company_name"])

        # ✅ Stock Data & Financial Statistics
        st.subheader("📈 Company Financial Data")
        if stock_ticker:
            try:
                stock_symbol = yf.Ticker(stock_ticker)
                stock_info = stock_symbol.info

                # ✅ Check if stock_info is available
                if stock_info and "regularMarketPrice" in stock_info:
                    st.write(f"**Stock Price ({stock_ticker}):** ${stock_info.get('regularMarketPrice', 'N/A')}")
                    st.write(f"**Market Cap:** ${stock_info.get('marketCap', 'N/A')}")
                    
                    # ✅ Fetch financial data (if available)
                    st.subheader("📊 Financial Statistics")
                    try:
                        financials = stock_symbol.financials
                        if financials is not None and not financials.empty:
                            st.write(financials)
                            # ✅ Plot Revenue & Net Income (if available)
                            if "Total Revenue" in financials.index and "Net Income" in financials.index:
                                fig, ax = plt.subplots(figsize=(8, 4))
                                ax.plot(financials.columns, financials.loc["Total Revenue"], label="Total Revenue", color="green")
                                ax.plot(financials.columns, financials.loc["Net Income"], label="Net Income", color="red")
                                ax.set_xlabel("Year")
                                ax.set_ylabel("USD ($)")
                                ax.legend()
                                st.pyplot(fig)
                        else:
                            st.warning("⚠️ No financial data available.")
                    except Exception:
                        st.warning("⚠️ Unable to fetch financial statistics.")

                else:
                    st.warning("⚠️ No stock data available.")

            except Exception as e:
                st.error(f"❌ Could not fetch stock data. Reason: {str(e)}")

            # ✅ Stock Price Chart
            st.subheader("📊 Stock Price Trend")
            try:
                stock_data = stock_symbol.history(period="6mo")
                if not stock_data.empty:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(stock_data.index, stock_data["Close"], label="Stock Price", color="blue")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Price (USD)")
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ No stock price data available.")

            except Exception as e:
                st.error(f"❌ Error fetching stock chart. Reason: {str(e)}")

        else:
            st.warning("⚠️ Data Not Available.")
