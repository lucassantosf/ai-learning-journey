import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 40000
});

export const healthCheck = async () => {
  try {
    const response = await api.get('/healthcheck');
    console.log('Health check response:', response.data);
    return response.status === 200 && response.data.status === 'ok';
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Health check failed:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        data: error.response?.data
      });
    } else {
      console.error('Unexpected health check error:', error);
    }
    return false;
  }
};

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    console.log('Uploading file:', file.name);
    console.log('FormData contents:', formData);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // Increase timeout for file uploads
      timeout: 30000,
    });

    console.log('Upload response:', response);

    return {
      success: true,
      data: response.data,
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error;
      
      console.error('Document upload failed:', {
        error: axiosError,
        config: axiosError.config,
        request: axiosError.request,
        response: axiosError.response,
      });

      if (axiosError.response) {
        // The request was made and the server responded with a status code
        console.error('Server responded with error:', axiosError.response.data);
        return {
          success: false,
          error: axiosError.response.data || axiosError.message,
        };
      } else if (axiosError.request) {
        // The request was made but no response was received
        console.error('No response received:', axiosError.request);
        return {
          success: false,
          error: 'Sem resposta do servidor',
        };
      } else {
        // Something happened in setting up the request
        console.error('Error setting up request:', axiosError.message);
        return {
          success: false,
          error: axiosError.message,
        };
      }
    } else {
      // Handle non-Axios errors
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Unexpected upload error:', errorMessage);
      return {
        success: false,
        error: errorMessage || 'Erro desconhecido no upload',
      };
    }
  }
};

export const queryAgent = async (question: string) => {
  try {
    const response = await api.post('/agent', { question: question });
    return {
      success: true,
      data: response.data
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error;
      console.error('Agent query failed:', {
        error: axiosError,
        response: axiosError.response,
      });

      // Extract error details more specifically
      const errorDetails = axiosError.response?.data;
      const errorMessage = typeof errorDetails === 'object' && errorDetails 
        ? (errorDetails.detail || errorDetails.message || JSON.stringify(errorDetails))
        : (axiosError.message || 'Erro na consulta ao agente');

      return {
        success: false,
        error: errorMessage,
        status: axiosError.response?.status
      };
    } else {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Unexpected agent query error:', errorMessage);
      return {
        success: false,
        error: errorMessage || 'Erro desconhecido na consulta'
      };
    }
  }
};

export interface QueryHistoryItem {
  id: number;
  question: string;
  answer: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export const getQueryHistory = async (limit: number = 20, keyword?: string) => {
  try {
    const response = await api.get('/query-history', {
      params: { 
        limit, 
        ...(keyword ? { keyword } : {}) 
      }
    });

    return {
      success: true,
      data: response.data
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error;
      console.error('Query history fetch failed:', {
        error: axiosError,
        response: axiosError.response,
      });

      return {
        success: false,
        error: axiosError.response?.data || axiosError.message || 'Erro ao buscar histórico de consultas'
      };
    } else {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Unexpected query history error:', errorMessage);
      return {
        success: false,
        error: errorMessage || 'Erro desconhecido ao buscar histórico'
      };
    }
  }
};

export const deleteQueryHistoryItem = async (queryId: number) => {
  try {
    const response = await api.delete(`/query-history/${queryId}`);
    return {
      success: true,
      data: response.data
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error;
      console.error('Delete query history item failed:', {
        error: axiosError,
        response: axiosError.response,
      });

      return {
        success: false,
        error: axiosError.response?.data || axiosError.message || 'Erro ao excluir item do histórico'
      };
    } else {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Unexpected delete query history error:', errorMessage);
      return {
        success: false,
        error: errorMessage || 'Erro desconhecido ao excluir item do histórico'
      };
    }
  }
};

export const clearQueryHistory = async () => {
  try {
    const response = await api.delete('/query-history');
    return {
      success: true,
      data: response.data
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error;
      console.error('Clear query history failed:', {
        error: axiosError,
        response: axiosError.response,
      });

      return {
        success: false,
        error: axiosError.response?.data || axiosError.message || 'Erro ao limpar histórico de consultas'
      };
    } else {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Unexpected clear query history error:', errorMessage);
      return {
        success: false,
        error: errorMessage || 'Erro desconhecido ao limpar histórico'
      };
    }
  }
};
