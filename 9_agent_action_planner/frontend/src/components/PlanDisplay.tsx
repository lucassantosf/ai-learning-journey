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

    return new Promise<void>((resolve, reject) => {
      // Criar um socket para receber atualizações em tempo real
      const socket = AgentService.connectToProgressWebSocket(
        (update) => {
          // Log para debug
          console.log('WebSocket Update:', update);

          // Tratar diferentes tipos de eventos do WebSocket
          switch (update.type) {
            case 'step_start':
              setExecutionProgress(prev => [
                ...prev, 
                `Iniciando Passo ${update.step}: ${update.description || ''}`
              ]);
              setCurrentStep(update.step ? update.step - 1 : null);
              break;

            case 'step_progress':
              setExecutionProgress(prev => [
                ...prev, 
                `Progresso Passo ${update.step}: ${update.message || update.progress || ''}`
              ]);
              setCurrentStep(update.step ? update.step - 1 : null);
              break;

            case 'step_complete':
              setExecutionProgress(prev => [
                ...prev, 
                `Passo ${update.step} concluído`
              ]);
              break;

            case 'step_error':
              setExecutionProgress(prev => [
                ...prev, 
                `Erro no Passo ${update.step}: ${update.error || 'Erro desconhecido'}`
              ]);
              break;

            default:
              // Mensagens genéricas de progresso
              if (update.message) {
                setExecutionProgress(prev => [...prev, update.message]);
              }
          }
        },
        // Callback de abertura do socket - CHAVE PRINCIPAL
        () => {
          // Iniciar execução do plano APÓS o socket estar aberto
          AgentService.executePlan(plan.plan_id)
            .then((response: ExecuteResponse) => {
              // Atualizar resultados da execução
              setExecutionResults(response.result.results);
              resolve();
            })
            .catch(error => {
              setExecutionError('Erro ao executar o plano');
              console.error(error);
              reject(error);
            });
        },
        // Callback de fechamento do socket
        () => {
          setIsExecuting(false);
          resolve();
        },
        // Callback de erro do socket
        (error) => {
          setExecutionError('Erro na conexão WebSocket');
          setIsExecuting(false);
          reject(error);
        }
      );

      // Configurar timeout para evitar execuções muito longas
      const timeoutId = setTimeout(() => {
        setExecutionError('Tempo limite de execução excedido');
        setIsExecuting(false);
        socket.close();
        reject(new Error('Timeout'));
      }, 60000); // 60 segundos

      // Limpar timeout quando a execução terminar
      socket.onclose = () => {
        clearTimeout(timeoutId);
      };
    });
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
                  {/* Substituir o placeholder por uma renderização condicional */}
                  {step.result ? (
                    <div 
                      className={styles.stepResultContent}
                      dangerouslySetInnerHTML={{ __html: step.result.replace(/\n/g, '<br/>') }}
                    />
                  ) : (
                    <p>Nenhum detalhe adicional disponível para este passo.</p>
                  )}
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