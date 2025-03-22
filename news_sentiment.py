import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
import pyttsx3
import os
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from news_scraper import get_news  # Import the scraper

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

def comparative_analysis(news_list):
    """Analyzes sentiment distribution and topic coverage."""
    try:
        if not news_list or "error" in news_list:
            return {"error": "No valid news data to analyze."}

        sentiment_counts = Counter([article["sentiment"] for article in news_list])

        # Extracting unique words from titles as topics
        topic_keywords = {}
        for article in news_list:
            words = article["title"].split()
            topic_keywords[article["title"]] = words  

        # Identifying common & unique topics
        common_topics = set.intersection(*map(set, topic_keywords.values()))
        unique_topics = {
            title: list(set(words) - common_topics)
            for title, words in topic_keywords.items()
        }

        # Final sentiment summary
        sentiment_summary = {
            "Sentiment Distribution": dict(sentiment_counts),
            "Coverage Differences": [
                {
                    "Comparison": f"Article '{a1['title']}' vs. Article '{a2['title']}'",
                    "Impact": f"One is {a1['sentiment']} while the other is {a2['sentiment']}.",
                }
                for i, a1 in enumerate(news_list)
                for j, a2 in enumerate(news_list)
                if i < j and a1["sentiment"] != a2["sentiment"]
            ],
            "Topic Overlap": {
                "Common Topics": list(common_topics),
                "Unique Topics": unique_topics,
            },
        }

        return sentiment_summary

    except Exception as e:
        return {"error": f"Exception in comparative analysis: {str(e)}"}

def text_to_speech(text, lang="en"):
    """Dual TTS: Uses `pyttsx3` for English and `Vosk` for Hindi."""
    try:
        if not text:
            return "Error: No text provided for speech conversion."

        filename = f"speech_output_{lang}.mp3"

        if lang == "en":
            # ✅ Use `pyttsx3` for English
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')

            for voice in voices:
                if "english" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break

            engine.setProperty("rate", 180)  # Adjust speech speed
            engine.save_to_file(text, filename)
            engine.runAndWait()

        else:
            # ✅ Use `Vosk` for Hindi
            model = AutoModelForSpeechSeq2Seq.from_pretrained("suno/bark")
            processor = AutoProcessor.from_pretrained("suno/bark")
            text_to_speech_pipeline = pipeline("text-to-speech", model=model, processor=processor)

            # Generate Hindi speech
            speech = text_to_speech_pipeline(text, return_tensors="pt")
            torchaudio.save(filename, speech["audio"], 24000)

        return filename  # Return saved file path

    except Exception as e:
        return f"Error in TTS conversion: {str(e)}"

# Full Pipeline: Get News, Analyze Sentiment, Generate Speech
if __name__ == "__main__":
    company = "Tesla"
    print(f"\n🔍 Fetching news for: {company}\n")

    news_data = get_news(company)
    print("\n📰 News Articles:\n", news_data)
    
    if "error" not in news_data:
        sentiment_report = comparative_analysis(news_data)
        print("\n📊 Sentiment Analysis Report:\n", sentiment_report)

        # Ask user for language preference
        language_choice = input("Enter 'hi' for Hindi or 'en' for English TTS: ").strip().lower()
        speech_output = text_to_speech(str(sentiment_report), lang=language_choice)
        print(f"\n🔊 Speech saved at: {speech_output}")
        os.system(f"start {speech_output}")  # Play the audio file (Windows)
