import React, { useState, useRef } from 'react';
import axios from 'axios';

const FileUpload = ({ selectedLanguage, onUploadStart, onTranslationComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

  // Configure API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    // Enhanced file validation
    const allowedExtensions = ['mp3', 'wav', 'mp4', 'avi', 'mov', 'm4a', 'ogg'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      setUploadError(`Please upload supported files: ${allowedExtensions.join(', ').toUpperCase()}`);
      return;
    }

    // File size validation (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setUploadError(`File size must be less than ${maxSize / (1024 * 1024)}MB. Current size: ${(file.size / (1024 * 1024)).toFixed(2)}MB`);
      return;
    }

    // Check if language is selected
    if (!selectedLanguage) {
      setUploadError('Please select a target language first');
      return;
    }

    setUploadError('');
    onUploadStart();

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('target_language', selectedLanguage);

      console.log(`Uploading ${file.name} for translation to ${selectedLanguage}`);

      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes timeout
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload Progress: ${percentCompleted}%`);
        }
      });

      if (response.data.status === 'success') {
        console.log('Translation successful:', response.data);
        onTranslationComplete(response.data);
      } else {
        setUploadError('Translation failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      
      let errorMessage = 'Upload failed. Please check your connection and try again.';
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.error || `Server Error: ${error.response.status}`;
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error. Please check if the backend server is running on port 5000.';
      } else if (error.code === 'ECONNABORTED') {
        // Timeout error
        errorMessage = 'Upload timeout. File might be too large or connection is slow.';
      }
      
      setUploadError(errorMessage);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="file-upload">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".mp3,.wav,.mp4,.avi,.mov,.m4a,.ogg"
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        <div className="upload-content">
          <span className="upload-icon">🎵</span>
          <h3>Drag and drop your audio/video file here</h3>
          <p>or click to select file</p>
          <div className="supported-formats">
            <small>Supported formats: MP3, WAV, MP4, AVI, MOV, M4A, OGG (Max: 50MB)</small>
          </div>
        </div>
      </div>
      
      {uploadError && (
        <div className="error-message">
          <strong>Error:</strong> {uploadError}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
