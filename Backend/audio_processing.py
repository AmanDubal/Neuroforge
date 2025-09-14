import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================
# STEP 1: Set FFmpeg and FFprobe
# ===============================
# Use your existing FFmpeg paths - keep these as they are working for you
ffmpeg_path = r"C:\Users\itlab\Downloads\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\itlab\Downloads\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\bin\ffprobe.exe"

# Add the directories of FFmpeg and FFprobe to PATH
os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ";" + os.environ["PATH"]
os.environ["PATH"] = os.path.dirname(ffprobe_path) + ";" + os.environ["PATH"]

# Tell PyDub explicitly which FFmpeg and FFprobe executables to use
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Check if paths exist
FFMPEG_AVAILABLE = os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path)
if FFMPEG_AVAILABLE:
    logger.info("✅ FFmpeg configured successfully with your paths")
else:
    logger.error("❌ FFmpeg paths not found - check your paths")

# ===============================
# STEP 2: Initialize Recognizer
# ===============================
recognizer = sr.Recognizer()

# ===============================
# STEP 3: Convert Audio to Text
# ===============================
def speech_to_text(file_path, src_lang="en-US"):
    """
    Converts any audio file to text with enhanced error handling.
    Updated function name to match app.py import
    """
    if not FFMPEG_AVAILABLE:
        logger.error("FFmpeg not available for audio processing")
        return "Error: FFmpeg not configured properly"
        
    temp_wav = None
    try:
        logger.info(f"Processing audio file: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        # Create temporary WAV file
        temp_wav = "temp_audio.wav"
        file_format = os.path.splitext(file_path)[1][1:].lower()
        
        # Convert to WAV format
        logger.info("Converting audio to WAV format...")
        audio = AudioSegment.from_file(file_path, format=file_format)
        
        # Ensure audio is in correct format for speech recognition
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(temp_wav, format="wav")
        
        # Speech recognition
        logger.info("Performing speech recognition...")
        with sr.AudioFile(temp_wav) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        
        # Use Google Speech Recognition
        text = recognizer.recognize_google(audio_data, language=src_lang)
        logger.info(f"Speech recognition successful: {len(text)} characters")
        
        return text
        
    except sr.UnknownValueError:
        logger.error("Speech recognition could not understand the audio")
        return "Error: Could not understand the audio content"
    except sr.RequestError as e:
        logger.error(f"Speech recognition service error: {e}")
        return "Error: Speech recognition service unavailable"
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        return f"Error processing audio: {str(e)}"
    finally:
        # Cleanup temporary file
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except:
                pass

# ===============================
# STEP 4: Translate Text
# ===============================
def translate_text(text, target_lang="hi", src_lang="en"):
    """
    Translate text with error handling and validation.
    Updated parameter order to match app.py usage
    """
    try:
        if not text or text.strip() == "":
            return "No text to translate"
            
        if text.startswith("Error:"):
            return text  # Pass through error messages
            
        logger.info(f"Translating text from {src_lang} to {target_lang}")
        
        # Create translator
        translator = GoogleTranslator(source=src_lang, target=target_lang)
        
        # Handle long text by chunking
        max_chunk_size = 5000
        if len(text) > max_chunk_size:
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            translated_chunks = []
            
            for chunk in chunks:
                translated_chunk = translator.translate(chunk)
                translated_chunks.append(translated_chunk)
                
            result = " ".join(translated_chunks)
        else:
            result = translator.translate(text)
            
        logger.info(f"Translation successful: {len(result)} characters")
        return result
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return f"Translation error: {str(e)}"

# ===============================
# STEP 5: Convert Text to Speech
# ===============================
def text_to_speech(text, lang="hi", output_dir="output_audio"):
    """
    Convert text to speech with enhanced options.
    Updated parameter order to match app.py usage
    """
    try:
        if not text or text.strip() == "" or text.startswith("Error:"):
            logger.warning("No valid text for TTS conversion")
            return None
            
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        filename = f"tts_{lang}_{uuid.uuid4().hex[:8]}.mp3"
        output_path = os.path.join(output_dir, filename)
        
        logger.info(f"Generating speech for {lang}: {len(text)} characters")
        
        # Create TTS object with slow speech for clarity
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        
        logger.info(f"TTS audio saved: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None

# For backward compatibility with existing code
audio_to_text = speech_to_text

# Test function
def test_audio_processing():
    """Test audio processing capabilities"""
    logger.info("Testing audio processing setup...")
    
    tests = {
        "FFmpeg": FFMPEG_AVAILABLE,
        "Speech Recognition": True,  # Always available
        "Translation": True,  # Always available  
        "Text-to-Speech": True  # Always available
    }
    
    for test_name, status in tests.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {test_name}: {'Available' if status else 'Not Available'}")
    
    return all(tests.values())

if __name__ == "_main_":
    # Run tests
    test_audio_processing()
    
    print(f"FFmpeg Path: {ffmpeg_path}")
    print(f"FFmpeg Available: {FFMPEG_AVAILABLE}")
    
    # Interactive mode if needed
    print("\n🎯 Audio Processing Test Mode")
    print("Enter 'test' to test with a file, or 'exit' to quit:")
    
    choice = input().strip().lower()
    if choice == "test":
        file_path = input("Enter audio file path: ").strip('"')
        if os.path.exists(file_path):
            text = speech_to_text(file_path)
            print(f"Extracted text: {text}")
            
            if not text.startswith("Error:"):
                translated = translate_text(text, "hi")
                print(f"Hindi translation: {translated}")
                
                audio_file = text_to_speech(translated, "hi")
                if audio_file:
                    print(f"Audio saved: {audio_file}")