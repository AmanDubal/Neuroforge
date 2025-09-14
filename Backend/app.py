from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid

# Import processing functions from Member 4
try:
    from audio_processing import speech_to_text, translate_text, text_to_speech
    PROCESSING_AVAILABLE = True
except ImportError:
    print("⚠️  audio_processing.py not found. Using mock responses.")
    PROCESSING_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'avi', 'mov'}

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',  # Change this!
    'database': 'neuroforge'
}

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None

def init_database():
    """Initialize database and create tables"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS neuroforge")
        cursor.execute("USE neuroforge")
        
        # Create table
        create_table = """
        CREATE TABLE IF NOT EXISTS translations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(100),
            original_filename VARCHAR(255),
            source_language VARCHAR(10) DEFAULT 'en',
            target_language VARCHAR(10),
            original_text TEXT,
            translated_text TEXT,
            audio_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("✅ Database initialized!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
init_database()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'message': 'Audio Translation API Running!',
        'version': '1.0'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        target_language = request.form.get('target_language', 'hi')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{session_id}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Process file (Member 4's functions)
        if PROCESSING_AVAILABLE:
            original_text = speech_to_text(file_path)
            translated_text = translate_text(original_text, target_language)
            audio_file_path = text_to_speech(translated_text, target_language)
        else:
            # Mock response for testing
            original_text = "This is sample English text from audio."
            translated_text = "यह ऑडियो से नमूना अंग्रेजी पाठ है।"
            audio_file_path = None
        
        # Save to database
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO translations 
            (session_id, original_filename, target_language, original_text, translated_text, audio_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                session_id, filename, target_language, 
                original_text, translated_text, audio_file_path
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
            'audio_available': audio_file_path is not None
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/languages', methods=['GET'])
def get_languages():
    languages = {
        'hi': 'Hindi',
        'mr': 'Marathi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'bn': 'Bengali',
        'gu': 'Gujarati'
    }
    return jsonify({'languages': languages})

@app.route('/history', methods=['GET'])
def get_history():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT session_id, original_filename, target_language, 
                       original_text, translated_text, created_at
                FROM translations ORDER BY created_at DESC LIMIT 20
            """)
            history = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify({'history': history})
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Audio Translation API...")
    print("📡 Available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)