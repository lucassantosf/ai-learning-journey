import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Configuration for API base settings
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: BASE_URL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor for request logging (optional)
    this.axiosInstance.interceptors.request.use(
      (config) => {
        console.log(`Sending request to: ${config.url}`, config.data);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor for response handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      this.handleError
    );
  }

  // Generic method for GET requests
  async get<T>(url: string, params?: any): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.get(url, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Generic method for POST requests
  async post<T>(url: string, data: any, config = {}): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.post(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Specific method for file upload
  async uploadDocument(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);

    return this.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }

  // Health check method
  async healthCheck(): Promise<any> {
    return this.get('/health');
  }

  // Error handling method
  private handleError(error: AxiosError): never {
    if (error.response) {
      // The request was made and the server responded with a status code
      console.error('API Error Response:', error.response.data);
      throw new Error(
        error.response.data?.detail || 
        error.response.data?.message || 
        'An unexpected error occurred'
      );
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something happened in setting up the request
      console.error('Error setting up request:', error.message);
      throw new Error('Error preparing the request');
    }
  }
}

// Export a singleton instance
export const apiService = new ApiService();