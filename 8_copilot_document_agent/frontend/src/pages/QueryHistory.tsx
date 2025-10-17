import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ArrowLeftOutlined from '@ant-design/icons/lib/icons/ArrowLeftOutlined';

interface HistoryItem {
  id: string;
  date: Date;
  question: string;
  answer: string;
  feedback?: 'positive' | 'negative';
}

const QueryHistory: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([
    // Simulated history items (will be replaced with actual backend data)
    {
      id: '1',
      date: new Date(),
      question: 'What is the main purpose of this document?',
      answer: 'The document discusses key strategies for project management.',
      feedback: undefined
    },
    {
      id: '2',
      date: new Date(),
      question: 'Can you summarize the key points?',
      answer: 'Here are the main points from the document...',
      feedback: 'positive'
    }
  ]);

  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null);

  const handleItemClick = (item: HistoryItem) => {
    setSelectedItem(item);
  };

  const handleFeedback = (feedback: 'positive' | 'negative') => {
    if (selectedItem) {
      setHistory(prev => 
        prev.map(item => 
          item.id === selectedItem.id 
            ? { ...item, feedback } 
            : item
        )
      );
      setSelectedItem(prevItem => 
        prevItem ? { ...prevItem, feedback } : null
      );
    }
  };

  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate('/');
  };

  return (
    <div className="query-history-container">
      <div className="query-history-header">
        <button 
          className="back-button" 
          onClick={handleGoBack}
        >
          <ArrowLeftOutlined /> Back to Home
        </button>
        <h2>Query History</h2>
      </div>
      
      <div className="history-list">
        {history.map((item) => (
          <div 
            key={item.id} 
            className={`history-item ${selectedItem?.id === item.id ? 'selected' : ''}`}
            onClick={() => handleItemClick(item)}
          >
            <div className="history-item-header">
              <span className="date">{item.date.toLocaleString()}</span>
              {item.feedback && (
                <span className={`feedback ${item.feedback}`}>
                  {item.feedback === 'positive' ? '👍' : '👎'}
                </span>
              )}
            </div>
            <p className="question">{item.question}</p>
          </div>
        ))}
      </div>

      {selectedItem && (
        <div className="history-details">
          <h3>Query Details</h3>
          <div className="detail-content">
            <p><strong>Question:</strong> {selectedItem.question}</p>
            <p><strong>Answer:</strong> {selectedItem.answer}</p>
            
            <div className="feedback-section">
              <p>Was this answer helpful?</p>
              <div className="feedback-buttons">
                <button 
                  onClick={() => handleFeedback('positive')}
                  className={selectedItem.feedback === 'positive' ? 'selected' : ''}
                >
                  👍 Yes
                </button>
                <button 
                  onClick={() => handleFeedback('negative')}
                  className={selectedItem.feedback === 'negative' ? 'selected' : ''}
                >
                  👎 No
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryHistory;
