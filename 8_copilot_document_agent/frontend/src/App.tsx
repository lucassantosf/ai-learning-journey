import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import DocumentUpload from './pages/DocumentUpload';
import ChatConsultation from './pages/ChatConsultation';
import QueryHistory from './pages/QueryHistory';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<DocumentUpload />} />
          <Route path="/chat" element={<ChatConsultation />} />
          <Route path="/history" element={<QueryHistory />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
