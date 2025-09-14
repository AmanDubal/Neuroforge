import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import TranslationResult from './components/TranslationResult';
import LanguageSelector from './components/LanguageSelector';
import './styles/App.css';

function App() {
  const [translationResult, setTranslationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('hi');

  const handleTranslationComplete = (result) => {
    setTranslationResult(result);
    setIsLoading(false);
  };

  const handleUploadStart = () => {
    setIsLoading(true);
    setTranslationResult(null);
  };

  const resetApp = () => {
    setTranslationResult(null);
    setIsLoading(false);
  };

  return (
    <div className="App">
      <div className="container">
        {/* Header */}
        <header className="app-header">
          <div className="header-content">
            <h1>🎧 Audio & Video Translator</h1>
            <p>Breaking language barriers in education</p>
          </div>
        </header>

        {/* Main Content */}
        <main className="main-content">
          {!translationResult && !isLoading && (
            <div className="upload-section">
              <div className="card">
                <h2>Upload Your Audio or Video</h2>
                <p>Convert English content to your regional language</p>
                
                <LanguageSelector 
                  selectedLanguage={selectedLanguage}
                  onLanguageChange={setSelectedLanguage}
                />
                
                <FileUpload 
                  selectedLanguage={selectedLanguage}
                  onUploadStart={handleUploadStart}
                  onTranslationComplete={handleTranslationComplete}
                />
              </div>
            </div>
          )}

          {isLoading && (
            <div className="loading-section">
              <div className="card">
                <div className="loading-spinner"></div>
                <h3>Processing your file...</h3>
                <p>Converting speech to text and translating</p>
              </div>
            </div>
          )}

          {translationResult && (
            <TranslationResult 
              result={translationResult}
              onReset={resetApp}
            />
          )}
        </main>

        {/* Features Section */}
        {!translationResult && !isLoading && (
          <section className="features">
            <h3>Features</h3>
            <div className="features-grid">
              <div className="feature-card">
                <span className="feature-icon">🎤</span>
                <h4>Speech Recognition</h4>
                <p>Advanced speech-to-text conversion</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🌍</span>
                <h4>Multi-language</h4>
                <p>Support for 6+ regional languages</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🔊</span>
                <h4>Audio Output</h4>
                <p>Text-to-speech in translated language</p>
              </div>
            </div>
          </section>
        )}

        {/* Footer */}
        <footer className="app-footer">
          <p>Built for hackathon • Making education accessible for all</p>
        </footer>
      </div>
    </div>
  );
}

export default App;