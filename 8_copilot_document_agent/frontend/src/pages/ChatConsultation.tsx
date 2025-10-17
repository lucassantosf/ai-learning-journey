import React, { useState } from 'react';
import { Link } from 'react-router-dom';

interface ChatMessage {
  text: string;
  type: 'user' | 'ai';
  sources?: string[];
}

const ChatConsultation: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    // User message
    const userMessage: ChatMessage = {
      text: question,
      type: 'user'
    };

    // Simulated AI response (will be replaced with actual backend call)
    const aiMessage: ChatMessage = {
      text: 'Simulated copilot response based on indexed documents.',
      type: 'ai',
      sources: ['document1.pdf', 'document2.docx']
    };

    setMessages(prev => [...prev, userMessage, aiMessage]);
    setQuestion('');
  };

  return (
    <div className="chat-consultation">
      <div className="chat-header">
        <Link to="/" className="back-button">
          <span className="back-button-icon">←</span>
          Back to Home
        </Link>
        <div className="header-spacer"></div>
        <h2>Copilot Consultation</h2>
      </div>
      
      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <div className="empty-chat-placeholder">
            <p>Start a conversation by asking a question about your documents</p>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`message ${msg.type}`}
              >
                <div className="message-content">
                  <p>{msg.text}</p>
                  {msg.type === 'ai' && msg.sources && (
                    <div className="sources">
                      <strong>Sources:</strong>
                      <ul>
                        {msg.sources.map((source, sourceIndex) => (
                          <li key={sourceIndex}>{source}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-container">
        <div className="chat-input">
          <input 
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents"
          />
          <button type="submit" disabled={!question.trim()}>
            <span className="send-icon">➤</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatConsultation;
