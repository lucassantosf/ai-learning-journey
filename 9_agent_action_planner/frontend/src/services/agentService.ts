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
  // Atualizar a interface para incluir mais tipos de eventos
  connectToProgressWebSocket(
    onMessage: (data: WebSocketMessage) => void, 
    onOpen?: () => void, 
    onClose?: () => void,
    onError?: (error: Event) => void
  ): WebSocket {
    const socket = new WebSocket(`ws://localhost:8000/api/v1/agent/ws/progress`);
    
    // Configurações para reconexão automática
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 3;
    const RECONNECT_DELAY = 3000; // 3 segundos

    socket.onopen = () => {
      console.group('WebSocket Connection');
      console.log('Connection established');
      console.log('Ready State:', socket.readyState);
      console.groupEnd();
      
      reconnectAttempts = 0; // Resetar tentativas de reconexão
      if (onOpen) onOpen();
    };

    socket.onmessage = (event) => {
      try {
        console.group('WebSocket Message');
        console.log('Raw message:', event.data);
        
        const data: WebSocketMessage = JSON.parse(event.data);
        
        // Normalização do evento
        const normalizedEvent: WebSocketMessage = {
          type: data.type || 'generic',
          message: data.message || '',
          timestamp: data.timestamp || new Date().toISOString(),
          step: data.step,
          description: data.description,
          progress: data.progress,
          error: data.error
        };

        console.log('Parsed message:', normalizedEvent);
        console.groupEnd();
        
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
      
      // Lógica de reconexão automática
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`Tentando reconectar (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
        
        setTimeout(() => {
          console.log('Reconectando WebSocket...');
          const newSocket = AgentService.connectToProgressWebSocket(
            onMessage, 
            onOpen, 
            onClose, 
            onError
          );
        }, RECONNECT_DELAY);
      }

      if (onClose) onClose();
    };

    // Método opcional para envio de mensagens
    (socket as any).sendMessage = (message: string) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ message }));
      }
    };

    return socket;
  }

  

};