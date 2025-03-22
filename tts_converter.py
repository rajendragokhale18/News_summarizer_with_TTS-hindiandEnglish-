from gtts import gTTS
import os

def text_to_speech(text, filename="output.mp3", lang="hi"):
    """Converts text to Hindi speech and saves as an MP3 file."""
    try:
        if not text:
            return "Error: No text provided for speech conversion."
        
        # Convert text to speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)

        return f"Speech saved successfully as {filename}"
    
    except Exception as e:
        return f"Error in TTS conversion: {str(e)}"

# Test the function
if __name__ == "__main__":
    sample_text = "गूगल एक बहुत बड़ी टेक्नोलॉजी कंपनी है।"
    print(text_to_speech(sample_text))
    os.system("start output.mp3")  # Play the audio file (Windows)
