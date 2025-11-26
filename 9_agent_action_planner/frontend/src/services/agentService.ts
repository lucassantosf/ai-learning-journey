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
  type: string;
  message: string;
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
  connectToProgressWebSocket(
    onMessage: (data: WebSocketMessage) => void, 
    onOpen?: () => void, 
    onClose?: () => void,
    onError?: (error: Event) => void
  ): WebSocket {
    const socket = new WebSocket(`ws://localhost:8000/api/v1/agent/ws/progress`);
    
    socket.onopen = () => {
      console.log('WebSocket connection established');
      if (onOpen) onOpen();
    };

    socket.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Erro ao processar mensagem WebSocket:', error);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event);
      if (onClose) onClose();
    };

    return socket;
  }
};