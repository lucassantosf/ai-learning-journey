import React, { useState } from 'react';
import { AgentService } from '../services/agentService';
import styles from './ChallengeInput.module.css';
import { motion } from 'framer-motion';

interface ChallengeInputProps {
  onPlanCreated: (plan: { 
    plan_id: number; 
    status: string;
    steps: string[] 
  }, challenge: string) => void;
}

const ChallengeInput: React.FC<ChallengeInputProps> = ({ onPlanCreated }) => {
  const [challenge, setChallenge] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!challenge.trim()) {
      setError('Por favor, insira um desafio');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const planResponse = await AgentService.createPlan(challenge);
      
      if (planResponse && planResponse.status === 'created') {
        // Passa o desafio junto com o plano
        onPlanCreated(planResponse, challenge);
        // Não limpa mais o input
      } else {
        throw new Error('Não foi possível criar o plano');
      }
    } catch (err) {
      console.error('Erro ao criar plano:', err);
      setError(err instanceof Error ? err.message : 'Não foi possível criar o plano. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div 
      className={styles.challengeContainer}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <form onSubmit={handleSubmit} className={styles.challengeForm}>
        <div className={styles.inputGroup}>
          <div className={styles.inputWrapper}>
            <input 
              type="text" 
              value={challenge}
              onChange={(e) => setChallenge(e.target.value)}
              placeholder="Descreva seu desafio ou objetivo"
              disabled={isLoading}
              className={`${styles.challengeInput} ${isLoading ? styles.disabled : ''}`}
            />
            <motion.button 
              type="submit" 
              disabled={isLoading}
              className={styles.submitButton}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isLoading ? (
                <div className={styles.spinner}></div>
              ) : (
                'Gerar Plano de Ação'
              )}
            </motion.button>
          </div>
          {error && (
            <motion.div 
              className={styles.errorMessage}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {error}
            </motion.div>
          )}
        </div>
      </form>
    </motion.div>
  );
};

export default ChallengeInput;
