import React from 'react';
import { Link } from 'react-router-dom';
import HealthCheck from '../components/HealthCheck';

const Home: React.FC = () => {
  return (
    <div className="home-container">

      <h1 className="home-title">Copilot Document Agent</h1>
      
      <HealthCheck />
      
      <div className="home-navigation">
        <Link to="/upload" className="nav-card">
          <div className="nav-card-icon">📤</div>
          <h2 className="nav-card-title">Document Upload</h2>
          <p className="nav-card-description">
            Upload and index your PDF and DOCX files for intelligent analysis
          </p>
        </Link>
        
        <Link to="/chat" className="nav-card">
          <div className="nav-card-icon">💬</div>
          <h2 className="nav-card-title">Copilot Consultation</h2>
          <p className="nav-card-description">
            Ask questions and get AI-powered insights from your documents
          </p>
        </Link>
        
        <Link to="/history" className="nav-card">
          <div className="nav-card-icon">📋</div>
          <h2 className="nav-card-title">Query History</h2>
          <p className="nav-card-description">
            Review past consultations and provide feedback to improve AI
          </p>
        </Link>
      </div>
    </div>
  );
};

export default Home;
