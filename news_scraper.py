import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon (if not already downloaded)
nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """Analyzes sentiment of a given text using VADER."""
    try:
        if not text:
            return "Neutral"
        
        sentiment_score = sia.polarity_scores(text)
        if sentiment_score["compound"] >= 0.05:
            return "Positive"
        elif sentiment_score["compound"] <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    except Exception as e:
        return f"Error: {str(e)}"

# NewsAPI Key
NEWSAPI_KEY = "2dcc448cf6f243579468f8d5a0dc3ba3"

def get_news(company_name, num_articles=10):
    """Fetches news articles for a given company using NewsAPI and analyzes sentiment."""
    try:
        url = f"https://newsapi.org/v2/everything?q={company_name}&language=en&sortBy=publishedAt&pageSize={num_articles}&apiKey={NEWSAPI_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            return {"error": f"Failed to fetch news (Status Code: {response.status_code})"}

        news_data = response.json()
        if news_data.get("status") != "ok":
            return {"error": "NewsAPI returned an error."}

        articles = news_data.get("articles", [])
        if not articles:
            return {"error": "No articles found."}

        news_list = [
            {
                "title": article["title"],
                "summary": article["description"] or "No summary available.",
                "link": article["url"],
                "sentiment": analyze_sentiment(article["title"])  # ✅ Apply sentiment analysis here
            }
            for article in articles
        ]

        return news_list

    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}

# Test function
if __name__ == "__main__":
    company = "Tesla"
    news_data = get_news(company)
    print(news_data)
