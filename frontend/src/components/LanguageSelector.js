import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LanguageSelector = ({ selectedLanguage, onLanguageChange }) => {
  const [languages, setLanguages] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      const response = await axios.get('/languages');
      if (response.data.languages) {
        setLanguages(response.data.languages);
      }
    } catch (error) {
      console.error('Error fetching languages:', error);
      // Fallback languages
      setLanguages({
        'hi': 'Hindi',
        'mr': 'Marathi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'bn': 'Bengali',
        'gu': 'Gujarati'
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="language-selector loading">Loading languages...</div>;
  }

  return (
    <div className="language-selector">
      <label htmlFor="language-select">
        <strong>Select Target Language:</strong>
      </label>
      <select
        id="language-select"
        value={selectedLanguage}
        onChange={(e) => onLanguageChange(e.target.value)}
        className="language-dropdown"
      >
        {Object.entries(languages).map(([code, name]) => (
          <option key={code} value={code}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;