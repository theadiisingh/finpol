import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Transaction API
export const transactionApi = {
  getAll: () => api.get('/transactions'),
  getById: (id: string) => api.get(`/transactions/${id}`),
  create: (data: any) => api.post('/transactions', data),
  analyze: (id: string) => api.post(`/transactions/${id}/analyze`),
}

// Compliance API
export const complianceApi = {
  getReports: () => api.get('/compliance/reports'),
  getReport: (id: string) => api.get(`/compliance/reports/${id}`),
  getRegulations: () => api.get('/compliance/regulations'),
  searchRegulations: (query: string) => api.get(`/compliance/search?q=${query}`),
}

// Health API
export const healthApi = {
  check: () => api.get('/health'),
}

export default api
