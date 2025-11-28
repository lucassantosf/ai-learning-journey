import axios from 'axios';

// Configuração base da API
const API_BASE_URL = 'http://localhost:8000/api/v1/agent';

// Interfaces para tipagem
interface PlanResponse {
  plan_id: number;
  status: string;
  steps: string[];
}

interface ExecuteResponse {
  result: any;
  status: string;
}

interface MemoryResponse {
  memory: any[];
}

interface WebSocketMessage {
  type: 'step_start' | 'step_progress' | 'step_complete' | 'step_error';
  step: number;
  description?: string;
  progress?: string;
  result?: any;
  error?: string;
  timestamp: string;
}

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

export const AgentService = {
  // Método para criar um plano
  async createPlan(prompt: string): Promise<PlanResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/plan`, { prompt });
      return response.data;
    } catch (error) {
      console.error('Erro ao criar plano:', error);
      throw error;
    }
  },

  // Método para executar um plano
  async executePlan(planId: number): Promise<ExecuteResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/execute`, { plan_id: planId });
      return response.data;
    } catch (error) {
      console.error('Erro ao executar plano:', error);
      throw error;
    }
  },

  async getMemory(): Promise<{ memory: MemoryEntry[] }> {
    const response = await axios.get(`${API_BASE_URL}/memory`);
    return response.data;
  },

  // Método para conexão WebSocket (progresso em tempo real)
  // Atualização do método connectToProgressWebSocket
  connectToProgressWebSocket(
    onMessage: (data: WebSocketMessage) => void, 
    onOpen?: () => void, 
    onClose?: () => void,
    onError?: (error: Event) => void
  ): WebSocket {
    const socket = new WebSocket(`ws://localhost:8000/api/v1/agent/ws/progress`);
    
    // Configurações para reconexão automática
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    const RECONNECT_DELAY = 3000; // 3 segundos
    let reconnectTimeout: NodeJS.Timeout | null = null;

    // Função para limpar timeout de reconexão
    const clearReconnectTimeout = () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }
    };

    socket.onopen = () => {
      console.group('WebSocket Connection');
      console.log('Connection established');
      console.log('Ready State:', socket.readyState);
      console.groupEnd();
      
      // Resetar tentativas de reconexão
      reconnectAttempts = 0;
      clearReconnectTimeout();
      
      if (onOpen) onOpen();
    };

    socket.onmessage = (event) => {
      try {
        console.group('WebSocket Message');
        console.log('Raw message:', event.data);
        
        const data = JSON.parse(event.data);
        
        // Normalização mais robusta do evento
        const normalizedEvent: WebSocketMessage = {
          type: data.type || 'generic',
          message: data.message || '',
          timestamp: data.timestamp || new Date().toISOString(),
          step: data.step,
          description: data.description,
          progress: data.progress,
          error: data.error,
          result: data.result
        };

        console.log('Parsed message:', normalizedEvent);
        console.groupEnd();
        
        // Filtrar e logar eventos específicos
        switch (normalizedEvent.type) {
          case 'step_start':
            console.log(`Starting step ${normalizedEvent.step}: ${normalizedEvent.description}`);
            break;
          case 'step_progress':
            console.log(`Progress for step ${normalizedEvent.step}: ${normalizedEvent.progress || normalizedEvent.message}`);
            break;
          case 'step_complete':
            console.log(`Step ${normalizedEvent.step} completed`);
            break;
          case 'step_error':
            console.error(`Error in step ${normalizedEvent.step}: ${normalizedEvent.error}`);
            break;
          case 'stream_error':
            console.error('Stream error:', normalizedEvent.error);
            break;
        }
        
        onMessage(normalizedEvent);
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
        console.error('Received data:', event.data);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event);
      
      // Lógica de reconexão automática com backoff exponencial
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        const delay = RECONNECT_DELAY * Math.pow(2, reconnectAttempts);
        
        console.log(`Tentando reconectar (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}) em ${delay}ms...`);
        
        clearReconnectTimeout();
        reconnectTimeout = setTimeout(() => {
          console.log('Reconectando WebSocket...');
          const newSocket = AgentService.connectToProgressWebSocket(
            onMessage, 
            onOpen, 
            onClose, 
            onError
          );
        }, delay);
      } else {
        console.error('Máximo de tentativas de reconexão excedido');
      }

      if (onClose) onClose();
    };

    // Método opcional para envio de mensagens
    (socket as any).sendMessage = (message: string) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ message }));
      } else {
        console.warn('Cannot send message. WebSocket is not open.');
      }
    };

    return socket;
  }

};