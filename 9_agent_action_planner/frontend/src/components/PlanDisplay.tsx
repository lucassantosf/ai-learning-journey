import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AgentService } from '../services/agentService';
import styles from './PlanDisplay.module.css';

interface PlanStep {
  step: number;
  description: string;
}

interface PlanDisplayProps {
  plan: {
    plan_id: number;
    status: string;
    steps: string[];
  };
}

interface ExecuteResponse {
  result: {
    plan_id: number;
    results: PlanStep[];
  };
}

const PlanDisplay: React.FC<PlanDisplayProps> = ({ plan }) => {
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionProgress, setExecutionProgress] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState<number | null>(null);
  const [executionError, setExecutionError] = useState<string | null>(null);
  const [executionResults, setExecutionResults] = useState<PlanStep[] | null>(null);
  const [expandedSteps, setExpandedSteps] = useState<{ [key: number]: boolean }>({});

  const handleExecutePlan = async () => {
    setIsExecuting(true);
    setExecutionProgress([]);
    setCurrentStep(null);
    setExecutionError(null);
    setExecutionResults(null);
    setExpandedSteps({});

    try {
      const socket = AgentService.connectToProgressWebSocket(
        (update) => {
          setExecutionProgress(prev => [...prev, update.message]);
          
          const stepMatch = update.message.match(/Passo (\d+)/);
          if (stepMatch) {
            setCurrentStep(parseInt(stepMatch[1], 10) - 1);
          }
        },
        () => {
          AgentService.executePlan(plan.plan_id)
            .then((response: ExecuteResponse) => {
              setExecutionResults(response.result.results);
            })
            .catch(error => {
              setExecutionError('Erro ao executar o plano');
              console.error(error);
            });
        },
        () => {
          setIsExecuting(false);
        },
        (error) => {
          setExecutionError('Erro na conexão WebSocket');
          setIsExecuting(false);
        }
      );

    } catch (error) {
      console.error('Erro ao executar plano:', error);
      setExecutionError('Não foi possível iniciar a execução do plano');
      setIsExecuting(false);
    }
  };

  useEffect(() => {
    if (executionResults) {
      setIsExecuting(false);
      const progressMessages = executionResults.map(
        step => `Passo ${step.step}: ${step.description}`
      );
      setExecutionProgress(progressMessages);
    }
  }, [executionResults]);

  const toggleStepExpansion = (stepNumber: number) => {
    setExpandedSteps(prev => ({
      ...prev,
      [stepNumber]: !prev[stepNumber]
    }));
  };

  return (
    <motion.div 
      className={styles.planDisplayContainer}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className={styles.planHeader}>
        <h2>Plano de Ação</h2>
        <span className={styles.planId}>Plano #{plan.plan_id}</span>
      </div>

      <motion.ul 
        className={styles.stepsList}
        initial="hidden"
        animate="visible"
        variants={{
          hidden: { opacity: 0 },
          visible: {
            opacity: 1,
            transition: {
              delayChildren: 0.2,
              staggerChildren: 0.1
            }
          }
        }}
      >
        {executionResults ? (
          executionResults.map((step) => (
            <motion.li 
              key={step.step}
              className={`
                ${styles.stepItem} 
                ${currentStep === step.step - 1 ? styles.currentStep : ''} 
                ${step.step < (currentStep || 0) ? styles.completedStep : ''}
              `}
              variants={{
                hidden: { opacity: 0, x: -20 },
                visible: { 
                  opacity: 1, 
                  x: 0,
                  transition: {
                    type: "spring",
                    stiffness: 100
                  }
                }
              }}
            >
              <div 
                className={styles.stepHeader}
                onClick={() => toggleStepExpansion(step.step)}
              >
                <div className={styles.stepNumber}>
                  {step.step}
                </div>
                <div className={styles.stepTitle}>
                  {step.description}
                </div>
                <div className={styles.expandIcon}>
                  {expandedSteps[step.step] ? '▼' : '►'}
                </div>
              </div>
              
              {expandedSteps[step.step] && (
                <motion.div 
                  className={styles.stepDetails}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Aqui você pode adicionar detalhes adicionais do passo */}
                  <p>Detalhes do passo {step.step} serão exibidos aqui.</p>
                </motion.div>
              )}
            </motion.li>
          ))
        ) : (
          plan.steps.map((step, index) => (
            <motion.li 
              key={index}
              className={styles.stepItem}
              variants={{
                hidden: { opacity: 0, x: -20 },
                visible: { 
                  opacity: 1, 
                  x: 0,
                  transition: {
                    type: "spring",
                    stiffness: 100
                  }
                }
              }}
            >
              <div className={styles.stepNumber}>
                {index + 1}
              </div>
              <div className={styles.stepContent}>
                {step}
              </div>
            </motion.li>
          ))
        )}
      </motion.ul>

      <div className={styles.actionButtons}>
        <button 
          className={styles.executeButton}
          onClick={handleExecutePlan}
          disabled={isExecuting}
        >
          {isExecuting ? 'Executando...' : 'Executar Plano'}
        </button>
      </div>

      <AnimatePresence>
        {(executionProgress.length > 0 || executionError) && (
          <motion.div 
            className={styles.executionProgressContainer}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h3>Progresso da Execução</h3>
            {executionError && (
              <div className={styles.errorMessage}>{executionError}</div>
            )}
            <ul>
              {executionProgress.map((progress, index) => (
                <motion.li 
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  {progress}
                </motion.li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default PlanDisplay;