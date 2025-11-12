import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { queryAgent } from '../services/api';

interface ChatMessage {
  text: string;
  type: 'user' | 'ai';
  sources?: string[];
  tools?: string[];
  loading?: true;
  error?: true;
}

const ChatConsultation: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedMessageIndex, setExpandedMessageIndex] = useState<number | null>(null);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    // Reset any previous error
    setErrorMessage(null);

    // User message
    const userMessage: ChatMessage = {
      text: question,
      type: 'user'
    };

    // Temporary AI message to show loading state
    const loadingMessage: ChatMessage = {
      text: 'Carregando...',
      type: 'ai',
      loading: true
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await queryAgent(question);

      if (response.success) {
        // Remove the loading message
        setMessages(prev => {
          const updatedMessages = prev.filter(msg => !msg.loading);
          
          // Safely extract response text
          let responseText = 'Não foi possível gerar uma resposta.';
          let sources: string[] = [];
          let tools: string[] = [];

          // Handle new response structure
          if (response.data) {
            if (response.data.answer && response.data.answer.final_answer) {
              responseText = response.data.answer.final_answer;
            } else if (typeof response.data.response === 'string') {
              responseText = response.data.response;
            }

            // Extract sources if available
            if (response.data.sources && Array.isArray(response.data.sources)) {
              sources = response.data.sources;
            }

            // Extract tools used if available
            if (response.data.answer && response.data.answer.tools_used) {
              tools = response.data.answer.tools_used;
            }
          }

          // Add the actual AI response
          const aiMessage: ChatMessage = {
            text: responseText,
            type: 'ai',
            sources: sources,
            tools: tools
          };

          return [...updatedMessages, aiMessage];
        });
      } else {
        // Handle error scenario
        setMessages(prev => {
          const updatedMessages = prev.filter(msg => !msg.loading);
          
          // Parse detailed error message
          let errorText = 'Erro na consulta';
          if (response.error) {
            if (typeof response.error === 'string') {
              errorText = response.error;
            } else if (Array.isArray(response.error)) {
              errorText = response.error.map(err => err.msg || err.message).join('; ');
            } else if (typeof response.error === 'object') {
              errorText = JSON.stringify(response.error);
            }
          }

          const errorMessage: ChatMessage = {
            text: errorText,
            type: 'ai',
            error: true
          };

          return [...updatedMessages, errorMessage];
        });

        // Set a more detailed error message
        setErrorMessage(response.error || 'Erro na consulta ao agente');
      }
    } catch (error) {
      // Unexpected error handling
      setMessages(prev => {
        const updatedMessages = prev.filter(msg => !msg.loading);
        
        const errorMessage: ChatMessage = {
          text: 'Erro inesperado. Tente novamente.',
          type: 'ai',
          error: true
        };

        return [...updatedMessages, errorMessage];
      });

      // Set a generic error message
      setErrorMessage('Erro inesperado. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  }, [question]);

  return (
    <div className="chat-consultation">
      <div className="chat-header">
        <Link to="/" className="back-button">
          <span className="back-button-icon">←</span>
          Voltar para Início
        </Link>
        <div className="header-spacer"></div>
        <h2>Consulta com Copilot</h2>
      </div>
      
      {errorMessage && (
        <div className="error-banner">
          <p>{errorMessage}</p>
          <button onClick={() => setErrorMessage(null)}>Fechar</button>
        </div>
      )}
      
      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <div className="empty-chat-placeholder">
            <p>Comece uma conversa fazendo uma pergunta sobre seus documentos</p>
            <div className="placeholder-tips">
              <p>💡 Dicas:</p>
              <ul>
                <li>Faça perguntas específicas sobre o conteúdo dos seus documentos</li>
                <li>Seja claro e direto na sua pergunta</li>
                <li>O Copilot irá buscar as informações relevantes para você</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`message ${msg.type} ${msg.loading ? 'loading' : ''} ${msg.error ? 'error' : ''}`}
              >
                <div className="message-content">
                  <p>{msg.text}</p>
                  {msg.type === 'ai' && !msg.loading && !msg.error && (
                    <>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="sources">
                          <strong>Fontes:</strong>
                          <ul>
                            {msg.sources.map((source, sourceIndex) => (
                              <li key={sourceIndex}>{source}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {msg.tools && msg.tools.length > 0 && (
                        <div 
                          className="tools-section"
                          onClick={() => {
                            // Toggle expanded state for this message
                            setExpandedMessageIndex(prevIndex => 
                              prevIndex === index ? null : index
                            );
                          }}
                        >
                          <strong>🛠️ Ferramentas Utilizadas</strong>
                          {expandedMessageIndex === index && (
                            <ul className="tools-list">
                              {msg.tools.map((tool, toolIndex) => (
                                <li key={toolIndex}>{tool}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      )}
                    </>
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
            placeholder="Faça uma pergunta sobre seus documentos"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={!question.trim() || isLoading}
          >
            <span className="send-icon">➤</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatConsultation;
