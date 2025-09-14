import React, { useState } from 'react';

const TranslationResult = ({ result, onReset }) => {
  const [showOriginal, setShowOriginal] = useState(true);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Text copied to clipboard!');
    });
  };

  const downloadResult = () => {
    const content = `Original Text:\n${result.original_text}\n\nTranslated Text:\n${result.translated_text}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `translation_${result.session_id}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="translation-result">
      <div className="result-card">
        <div className="result-header">
          <h2>✅ Translation Complete!</h2>
          <button className="btn-secondary" onClick={onReset}>
            Translate Another File
          </button>
        </div>

        <div className="toggle-section">
          <div className="toggle-buttons">
            <button
              className={`toggle-btn ${showOriginal ? 'active' : ''}`}
              onClick={() => setShowOriginal(true)}
            >
              Original (English)
            </button>
            <button
              className={`toggle-btn ${!showOriginal ? 'active' : ''}`}
              onClick={() => setShowOriginal(false)}
            >
              Translated ({result.target_language.toUpperCase()})
            </button>
          </div>
        </div>

        <div className="text-display">
          {showOriginal ? (
            <div className="text-content">
              <h3>Original Text:</h3>
              <p className="text-box">{result.original_text}</p>
              <button 
                className="copy-btn" 
                onClick={() => copyToClipboard(result.original_text)}
              >
                📋 Copy
              </button>
            </div>
          ) : (
            <div className="text-content">
              <h3>Translated Text:</h3>
              <p className="text-box translated">{result.translated_text}</p>
              <button 
                className="copy-btn" 
                onClick={() => copyToClipboard(result.translated_text)}
              >
                📋 Copy
              </button>
            </div>
          )}
        </div>

        {result.audio_available && (
          <div className="audio-section">
            <h3>🔊 Listen to Translation:</h3>
            <div className="audio-controls">
              <button className="play-btn">▶️ Play Audio</button>
              <small>Text-to-speech in target language</small>
            </div>
          </div>
        )}

        <div className="result-actions">
          <button className="btn-primary" onClick={downloadResult}>
            💾 Download Translation
          </button>
          <button className="btn-secondary" onClick={onReset}>
            🔄 Translate Another
          </button>
        </div>

        <div className="result-info">
          <small>Session ID: {result.session_id}</small>
        </div>
      </div>
    </div>
  );
};

export default TranslationResult;