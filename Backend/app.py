from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import processing functions from Member 4
try:
    from audio_processing import speech_to_text, translate_text, text_to_speech
    PROCESSING_AVAILABLE = True
    logger.info("✅ Audio processing modules loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Audio processing modules not available: {e}")
    PROCESSING_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'avi', 'mov', 'm4a', 'ogg'}

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Configuration - using neuroforge as requested
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',  # Change this to your actual password
    'database': 'neuroforge',  # Using neuroforge as requested
    'port': 3306
}

def get_db_connection():
    """Create database connection with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("✅ Database connected successfully")
            return connection
        except mysql.connector.Error as err:
            logger.error(f"Database connection attempt {attempt + 1} failed: {err}")
            if attempt == max_retries - 1:
                raise
    return None

def init_database():
    """Initialize database and create tables"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS neuroforge")
            cursor.execute("USE neuroforge")
            
            # Create table with improved schema
            create_table = """
            CREATE TABLE IF NOT EXISTS translations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                original_filename VARCHAR(255),
                source_language VARCHAR(10) DEFAULT 'en',
                target_language VARCHAR(10) NOT NULL,
                original_text TEXT,
                translated_text TEXT,
                audio_path VARCHAR(255),
                file_size BIGINT,
                processing_time DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session (session_id),
                INDEX idx_created (created_at),
                INDEX idx_language (target_language)
            )
            """
            cursor.execute(create_table)
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("✅ Database 'neuroforge' initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
init_database()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'message': 'Audio Translation API Running!',
        'version': '1.0',
        'database': 'neuroforge',
        'processing_available': PROCESSING_AVAILABLE,
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    start_time = datetime.now()
    
    try:
        # Validate file presence
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        target_language = request.form.get('target_language', 'hi')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not supported. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Validate language
        supported_languages = get_supported_languages()
        if target_language not in supported_languages:
            return jsonify({
                'error': f'Language not supported. Use one of: {", ".join(supported_languages.keys())}'
            }), 400

        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{session_id}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"File saved: {unique_filename} ({file_size} bytes)")

        # Process file
        if PROCESSING_AVAILABLE:
            try:
                logger.info("Starting audio processing...")
                original_text = speech_to_text(file_path)
                logger.info(f"Speech-to-text completed: {original_text[:50]}...")
                
                translated_text = translate_text(original_text, target_language)
                logger.info(f"Translation completed: {translated_text[:50]}...")
                
                audio_file_path = text_to_speech(translated_text, target_language)
                logger.info(f"Text-to-speech completed: {audio_file_path}")
                
            except Exception as e:
                logger.error(f"Processing error: {e}")
                # Fallback to mock data if processing fails
                original_text = f"Processing failed for {filename}"
                translated_text = f"Error: Could not process audio file"
                audio_file_path = None
        else:
            # Mock response for testing
            original_text = f"Sample English text extracted from {filename}"
            translated_text = get_sample_translation(target_language)
            audio_file_path = None

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Save to database
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO translations
            (session_id, original_filename, target_language, original_text, 
             translated_text, audio_path, file_size, processing_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                session_id, filename, target_language,
                original_text, translated_text, audio_file_path,
                file_size, processing_time
            ))
            connection.commit()
            cursor.close()
            connection.close()

        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'original_text': original_text,
            'translated_text': translated_text,
            'target_language': target_language,
            'audio_available': audio_file_path is not None,
            'processing_time': processing_time,
            'file_size': file_size
        })

    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

def get_supported_languages():
    """Get supported languages dictionary"""
    return {
        'hi': 'Hindi (हिंदी)',
        'mr': 'Marathi (मराठी)', 
        'ta': 'Tamil (தமிழ்)',
        'te': 'Telugu (తెలుగు)',
        'bn': 'Bengali (বাংলা)',
        'gu': 'Gujarati (ગુજરાતી)',
        'kn': 'Kannada (ಕನ್ನಡ)',
        'ml': 'Malayalam (മലയാളം)',
        'or': 'Odia (ଓଡ଼ିଆ)',
        'pa': 'Punjabi (ਪੰਜਾਬੀ)',
        'ur': 'Urdu (اردو)',
        'as': 'Assamese (অসমীয়া)'
    }

def get_sample_translation(target_lang):
    """Get sample translations for testing"""
    samples = {
        'hi': 'यह ऑडियो फाइल से निकाला गया नमूना पाठ है।',
        'mr': 'हा ऑडिओ फाइलमधून काढलेला नमुना मजकूर आहे।',
        'ta': 'இது ஆடியோ கோப்பிலிருந்து பிரித்தெடுக்கப்பட்ட மாதிரி உரை.',
        'te': 'ఇది ఆడియో ఫైల్ నుండి సంగ్రహించిన నమూనా పాఠం.',
        'bn': 'এটি অডিও ফাইল থেকে নিষ্কাশিত নমুনা পাঠ।',
        'gu': 'આ ઑડિઓ ફાઇલમાંથી કાઢેલો નમૂનો ટેક્સ્ટ છે।'
    }
    return samples.get(target_lang, 'Sample translated text')

@app.route('/languages', methods=['GET'])
def get_languages():
    languages = get_supported_languages()
    return jsonify({
        'languages': languages,
        'total': len(languages)
    })

@app.route('/history', methods=['GET'])
def get_history():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
            SELECT session_id, original_filename, target_language,
                   original_text, translated_text, file_size, 
                   processing_time, created_at
            FROM translations 
            ORDER BY created_at DESC 
            LIMIT 50
            """)
            history = cursor.fetchall()
            
            # Format datetime for JSON serialization
            for record in history:
                if record['created_at']:
                    record['created_at'] = record['created_at'].isoformat()
            
            cursor.close()
            connection.close()
            return jsonify({
                'history': history,
                'total': len(history)
            })
        
        return jsonify({'error': 'Database connection failed'}), 500
        
    except Exception as e:
        logger.error(f"History retrieval failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error occurred.'}), 500

if __name__ == '_main_':
    logger.info("🚀 Starting Audio Translation API...")
    logger.info("📡 Available at: http://localhost:5000")
    logger.info(f"🗄️  Database: neuroforge")
    logger.info(f"🔧 Processing available: {PROCESSING_AVAILABLE}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)