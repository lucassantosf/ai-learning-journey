import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  getQueryHistory, 
  deleteQueryHistoryItem, 
  clearQueryHistory, 
  type QueryHistoryItem 
} from '../services/api';

const QueryHistory: React.FC = () => {
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([]);
  const [selectedQuery, setSelectedQuery] = useState<QueryHistoryItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [keyword, setKeyword] = useState('');

  const fetchQueryHistory = async (searchKeyword?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getQueryHistory(20, searchKeyword);
      
      if (response.success) {
        setQueryHistory(response.data.queries);
      } else {
        setError(response.error || 'Erro ao buscar histórico');
      }
    } catch (err) {
      setError('Erro inesperado ao buscar histórico');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueryHistory();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchQueryHistory(keyword);
  };

  const handleDeleteItem = async (queryId: number) => {
    const confirmDelete = window.confirm('Tem certeza que deseja excluir esta consulta do histórico?');
    
    if (confirmDelete) {
      try {
        const response = await deleteQueryHistoryItem(queryId);
        
        if (response.success) {
          // Remove the deleted item from the list
          setQueryHistory(prev => prev.filter(query => query.id !== queryId));
          
          // Clear selected query if it was the deleted one
          if (selectedQuery?.id === queryId) {
            setSelectedQuery(null);
          }
        } else {
          setError(response.error || 'Erro ao excluir item do histórico');
        }
      } catch (err) {
        setError('Erro inesperado ao excluir item');
        console.error(err);
      }
    }
  };

  const handleClearHistory = async () => {
    const confirmClear = window.confirm('Tem certeza que deseja limpar todo o histórico de consultas?');
    
    if (confirmClear) {
      try {
        const response = await clearQueryHistory();
        
        if (response.success) {
          setQueryHistory([]);
          setSelectedQuery(null);
        } else {
          setError(response.error || 'Erro ao limpar histórico');
        }
      } catch (err) {
        setError('Erro inesperado ao limpar histórico');
        console.error(err);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short'
    });
  };

  return (
    <div className="query-history-container">
      <div className="query-history-header">
        <Link to="/" className="back-button">
          <span className="back-button-icon">←</span>
          Voltar para Início
        </Link>
        <h2>Histórico de Consultas</h2>
      </div>

      <div className="query-history-actions">
        <form onSubmit={handleSearch} className="search-form">
          <input 
            type="text" 
            placeholder="Buscar por palavra-chave" 
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <button type="submit">Buscar</button>
        </form>
        {queryHistory.length > 0 && (
          <button 
            className="clear-history-button" 
            onClick={handleClearHistory}
          >
            Limpar Histórico
          </button>
        )}
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="loading-spinner">Carregando...</div>
      ) : queryHistory.length === 0 ? (
        <div className="empty-history">
          <p>Nenhuma consulta encontrada</p>
        </div>
      ) : (
        <div className="history-list">
          {queryHistory.map((query) => (
            <div 
              key={query.id} 
              className={`history-item ${selectedQuery?.id === query.id ? 'selected' : ''}`}
              onClick={() => setSelectedQuery(query)}
            >
              <div className="history-item-header">
                <span className="date">{formatDate(query.created_at)}</span>
                <button 
                  className="delete-item-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteItem(query.id);
                  }}
                >
                  🗑️
                </button>
              </div>
              <p className="question">{query.question}</p>
            </div>
          ))}
        </div>
      )}

      {selectedQuery && (
        <div className="history-details">
          <h3>Detalhes da Consulta</h3>
          <div className="detail-content">
            <p><strong>Pergunta:</strong> {selectedQuery.question}</p>
            <p><strong>Resposta:</strong> {selectedQuery.answer}</p>
            <p><strong>Data:</strong> {formatDate(selectedQuery.created_at)}</p>
            {selectedQuery.metadata && Object.keys(selectedQuery.metadata).length > 0 && (
              <div className="metadata">
                <strong>Metadados:</strong>
                <div className="metadata-content">
                  {Object.entries(selectedQuery.metadata).map(([key, value]) => (
                    <div key={key} className="metadata-item">
                      <span className="metadata-key">{key}:</span>
                      <div className="metadata-value">
                        {typeof value === 'object' 
                          ? <pre>{JSON.stringify(value, null, 2)}</pre>
                          : String(value)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryHistory;
