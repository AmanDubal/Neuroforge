import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LanguageSelector = ({ selectedLanguage, onLanguageChange }) => {
  const [languages, setLanguages] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Configure API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.get(`${API_BASE_URL}/languages`, {
        timeout: 10000, // 10 seconds timeout
      });
      
      if (response.data.languages) {
        setLanguages(response.data.languages);
        console.log('Languages loaded:', response.data.languages);
      } else {
        throw new Error('No languages data received');
      }
    } catch (error) {
      console.error('Error fetching languages:', error);
      setError('Failed to load languages from server');
      
      // Fallback languages with expanded support
      setLanguages({
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
      });
      
      console.log('Using fallback languages');
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = (event) => {
    const newLanguage = event.target.value;
    console.log('Language changed to:', newLanguage, languages[newLanguage]);
    onLanguageChange(newLanguage);
  };

  if (loading) {
    return (
      <div className="language-selector loading">
        <div className="loading-spinner"></div>
        <p>Loading supported languages...</p>
      </div>
    );
  }

  return (
    <div className="language-selector">
      <label htmlFor="language-select">
        🌐 Select Target Language:
      </label>
      <select
        id="language-select"
        className="language-dropdown"
        value={selectedLanguage}
        onChange={handleLanguageChange}
      >
        <option value="" disabled>
          Choose a language...
        </option>
        {Object.entries(languages).map(([code, name]) => (
          <option key={code} value={code}>
            {name}
          </option>
        ))}
      </select>
      
      {error && (
        <div className="error-message" style={{ marginTop: '10px', fontSize: '0.9rem' }}>
          ⚠️ {error} (using offline languages)
        </div>
      )}
      
      {selectedLanguage && (
        <div style={{ marginTop: '10px', color: '#666', fontSize: '0.9rem' }}>
          ✅ Selected: <strong>{languages[selectedLanguage]}</strong>
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;
