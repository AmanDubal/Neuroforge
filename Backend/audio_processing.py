import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment

# ===============================
# STEP 1: Set FFmpeg and FFprobe
# ===============================
# PyDub uses FFmpeg (or avconv) to process audio files. 
# We need to provide the full path to FFmpeg/FFprobe executables
# and make sure Python can find them via the PATH variable.

ffmpeg_path  = r"C:\Users\itlab\Downloads\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\itlab\Downloads\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\bin\ffprobe.exe"

# Add the directories of FFmpeg and FFprobe to PATH
os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ";" + os.environ["PATH"]
os.environ["PATH"] = os.path.dirname(ffprobe_path) + ";" + os.environ["PATH"]

# Tell PyDub explicitly which FFmpeg and FFprobe executables to use
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe   = ffprobe_path

# ===============================
# STEP 2: Initialize Recognizer
# ===============================
# SpeechRecognition needs a recognizer object to process audio
recognizer = sr.Recognizer()

# ===============================
# STEP 3: Convert Audio to Text
# ===============================
def audio_to_text(file_path, src_lang="en-US"):
    """
    Converts any audio file to text.
    
    1. Detects file format from extension (mp3, wav, m4a, ogg, etc.)
    2. Converts the audio to WAV format (needed for SpeechRecognition)
    3. Uses Google Speech Recognition to convert audio to text
    """
    wav_file = "temp.wav"  # Temporary file for WAV conversion
    
    # Detect audio format automatically
    file_format = os.path.splitext(file_path)[1][1:].lower()
    
    # Convert input audio to WAV using PyDub + FFmpeg
    AudioSegment.from_file(file_path, format=file_format).export(wav_file, format="wav")
    
    # Load WAV file and recognize speech
    with sr.AudioFile(wav_file) as source:
        audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language=src_lang)

# ===============================
# STEP 4: Translate Text
# ===============================
def translate_text(text, src_lang="en", target_lang="hi"):
    """
    Translates text from source language to target language using GoogleTranslator.
    Example: English -> Hindi, Hindi -> English, French -> Spanish, etc.
    """
    return GoogleTranslator(source=src_lang, target=target_lang).translate(text)

# ===============================
# STEP 5: Convert Text to Speech
# ===============================
def text_to_speech(text, lang="hi", out_file="output.mp3"):
    """
    Converts text to speech using gTTS (Google Text-to-Speech)
    Saves the spoken audio as an MP3 file.
    """
    tts = gTTS(text=text, lang=lang)
    tts.save(out_file)
    return out_file

# ===============================
# STEP 6: Main Program
# ===============================
if __name__ == "__main__":
    # Input: audio file path
    input_file = input("Enter full path to your audio file: ").strip('"')
    
    # Input: source and target language codes
    # Example codes: 'en' for English, 'hi' for Hindi, 'es' for Spanish, 'fr' for French
    source_lang = input("Enter source language code (e.g., 'en' for English): ")
    target_lang = input("Enter target language code (e.g., 'hi' for Hindi): ")

    # Step 1: Convert audio to text
    print("🎤 Converting speech to text...")
    text = audio_to_text(input_file, src_lang=source_lang+"-US")  # Google Speech expects format like 'en-US'
    print("📝 Text:", text)

    # Step 2: Translate the text
    print("🌐 Translating...")
    translated = translate_text(text, src_lang=source_lang, target_lang=target_lang)
    print(f"🔤 Translated Text ({target_lang}):", translated)

    # Step 3: Convert translated text back to speech
    print("🔊 Converting back to speech...")
    output = text_to_speech(translated, lang=target_lang)
    print("✅ Saved:", output)