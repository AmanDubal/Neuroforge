-- Audio & Video Translation System Database
CREATE DATABASE IF NOT EXISTS neuroforge;
USE neuroforge;

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
);

-- Sample data for testing
INSERT INTO translations (session_id, original_filename, target_language, original_text, translated_text)
VALUES
('sample-1', 'test.mp3', 'hi', 'Hello world', 'नमस्ते दुनिया'),
('sample-2', 'demo.wav', 'mr', 'Good morning', 'शुभ सकाळ');