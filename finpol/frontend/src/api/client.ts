import axios, { AxiosError } from 'axios';
import { toast } from 'sonner';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const message = error.response?.data 
      ? JSON.stringify(error.response.data) 
      : error.message;
    
    toast.error(`API Error: ${message}`);
    return Promise.reject(error);
  }
);
