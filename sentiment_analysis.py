import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon (needed for sentiment analysis)
nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """Analyzes sentiment of a given text using VADER."""
    try:
        if not text:
            return "Neutral"  # Default to neutral if no text
        
        # Get sentiment scores
        sentiment_score = sia.polarity_scores(text)

        # Classify sentiment based on compound score
        if sentiment_score["compound"] >= 0.05:
            return "Positive"
        elif sentiment_score["compound"] <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    except Exception as e:
        return f"Error: {str(e)}"

# Test the function
if __name__ == "__main__":
    sample_text = "Tesla stocks are surging due to record-breaking sales!"
    print(analyze_sentiment(sample_text))
