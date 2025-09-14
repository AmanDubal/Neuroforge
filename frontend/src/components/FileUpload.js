import React, { useState, useRef } from 'react';
import axios from 'axios';

const FileUpload = ({ selectedLanguage, onUploadStart, onTranslationComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

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
    // Validate file type
    const allowedTypes = ['audio/mp3', 'audio/wav', 'video/mp4', 'video/avi', 'video/mov'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['mp3', 'wav', 'mp4', 'avi', 'mov'];
    
    if (!allowedExtensions.includes(fileExtension)) {
      setUploadError('Please upload MP3, WAV, MP4, AVI, or MOV files only');
      return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      setUploadError('File size must be less than 50MB');
      return;
    }

    setUploadError('');
    onUploadStart();

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('target_language', selectedLanguage);

      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.status === 'success') {
        onTranslationComplete(response.data);
      } else {
        setUploadError('Translation failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(
        error.response?.data?.error || 
        'Upload failed. Please check your connection and try again.'
      );
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
          accept=".mp3,.wav,.mp4,.avi,.mov"
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <h3>Drag & Drop your file here</h3>
          <p>or click to select file</p>
          <div className="supported-formats">
            <small>Supported: MP3, WAV, MP4, AVI, MOV (Max: 50MB)</small>
          </div>
        </div>
      </div>

      {uploadError && (
        <div className="error-message">
          ❌ {uploadError}
        </div>
      )}
    </div>
  );
};

export default FileUpload;