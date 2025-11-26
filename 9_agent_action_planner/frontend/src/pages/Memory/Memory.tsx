import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { AgentService } from '../../services/agentService';
import { Link } from 'react-router-dom';
import styles from './Memory.module.css';

interface MemoryEntry {
  id: number;
  type: string;
  content: {
    plan_id?: number;
    prompt?: string;
    step?: number;
    description?: string;
  };
  created_at?: string;
}

interface GroupedPlanMemory {
  plan_id: number;
  prompt?: string;
  entries: MemoryEntry[];
  created_at?: string;
}

const Memory: React.FC = () => {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMemory = async () => {
      try {
        const response = await AgentService.getMemory();
        setMemories(response.memory);
        setIsLoading(false);
      } catch (err) {
        console.error('Erro ao buscar memória:', err);
        setError('Não foi possível carregar o histórico');
        setIsLoading(false);
      }
    };

    fetchMemory();
  }, []);

  const groupedMemories = useMemo(() => {
    const grouped: { [key: number]: GroupedPlanMemory } = {};

    memories.forEach(entry => {
      if (entry.content.plan_id) {
        if (!grouped[entry.content.plan_id]) {
          grouped[entry.content.plan_id] = {
            plan_id: entry.content.plan_id,
            prompt: entry.content.prompt,
            entries: [],
            created_at: entry.created_at
          };
        }
        grouped[entry.content.plan_id].entries.push(entry);
      }
    });

    return Object.values(grouped).sort((a, b) => 
      new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
    );
  }, [memories]);

  const formatDate = (dateString?: string) => {
    return dateString 
      ? new Date(dateString).toLocaleString('pt-BR', {
          dateStyle: 'medium',
          timeStyle: 'short'
        }) 
      : 'Data não disponível';
  };

  const renderMemoryEntryContent = (entry: MemoryEntry) => {
    switch (entry.type) {
      case 'execution_summary':
        return <p>Resumo de Execução</p>;
      case 'reflection':
        return <p>Reflexão: {entry.content.description || 'Sem detalhes'}</p>;
      case 'step_started':
        return <p>Passo {entry.content.step} Iniciado</p>;
      case 'step_result':
        return <p>Resultado do Passo {entry.content.step}: {entry.content.description || 'Sem descrição'}</p>;
      default:
        return <p>Entrada não reconhecida</p>;
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p>Carregando histórico...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <p>{error}</p>
        <Link to="/" className={styles.backLink}>Voltar para Início</Link>
      </div>
    );
  }

  return (
    <motion.div 
      className={styles.memoryContainer}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className={styles.header}>
        <Link to="/" className={styles.backLink}>← Voltar</Link>
        <h1>Histórico de Memória do Agente</h1>
      </header>

      {groupedMemories.length === 0 ? (
        <div className={styles.emptyState}>
          <p>Nenhum histórico de memória encontrado</p>
        </div>
      ) : (
        <div className={styles.memoryList}>
          {groupedMemories.map((planMemory) => (
            <motion.div 
              key={planMemory.plan_id} 
              className={styles.planMemoryGroup}
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className={styles.planHeader}>
                <h2>Plano #{planMemory.plan_id}</h2>
                <span className={styles.timestamp}>
                  {formatDate(planMemory.created_at)}
                </span>
              </div>
              
              {planMemory.prompt && (
                <div className={styles.planPrompt}>
                  <strong>Desafio:</strong> {planMemory.prompt}
                </div>
              )}

              <ul className={styles.planEntries}>
                {planMemory.entries.map((entry) => (
                  <li key={entry.id} className={styles.planEntry}>
                    {renderMemoryEntryContent(entry)}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default Memory;