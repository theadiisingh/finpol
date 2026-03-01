import { apiClient } from './client';
import { 
  Transaction, 
  TransactionCreate, 
  RiskResponse, 
  Regulation, 
  ComplianceReport,
  DashboardStats 
} from '../types';

// Transaction APIs
export const transactionApi = {
  // Create a new transaction with risk assessment
  create: async (data: TransactionCreate): Promise<Transaction> => {
    const response = await apiClient.post<Transaction>('/transactions', data);
    return response.data;
  },

  // Get all transactions with pagination
  getAll: async (limit: number = 100, offset: number = 0): Promise<Transaction[]> => {
    const response = await apiClient.get<Transaction[]>(`/transactions?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  // Get a single transaction by ID
  getById: async (id: string): Promise<Transaction> => {
    const response = await apiClient.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },

  // Analyze a transaction for risk and compliance
  analyze: async (transaction: {
    transaction_id?: string;
    user_id: string;
    amount: number;
    currency: string;
    transaction_type: string;
    country: string;
    merchant_type: string;
    device_risk_score: number;
  }): Promise<RiskResponse> => {
    const response = await apiClient.post<RiskResponse>('/transactions/analyze', transaction);
    return response.data;
  },

  // Delete a transaction
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/transactions/${id}`);
  },
};

// Compliance APIs
export const complianceApi = {
  // Get all regulations
  getRegulations: async (): Promise<Regulation[]> => {
    const response = await apiClient.get<Regulation[]>('/compliance/regulations');
    return response.data;
  },

  // Search regulations
  searchRegulations: async (query: string): Promise<Regulation[]> => {
    const response = await apiClient.post<{ content: string; source: string }[]>(
      '/compliance/regulations/search',
      { query }
    );
    return response.data.map((item, index) => ({
      id: `reg-${index}`,
      title: `Regulation ${index + 1}`,
      content: item.content,
      source: item.source,
    }));
  },

  // Generate compliance report
  generateReport: async (transactionId: string, riskScore: number, riskLevel: string): Promise<ComplianceReport> => {
    const response = await apiClient.post<ComplianceReport>(
      `/compliance/report/${transactionId}?risk_score=${riskScore}&risk_level=${riskLevel}`
    );
    return response.data;
  },

  // Upload file for bulk processing
  uploadFile: async (file: File, userId: string = "bulk_upload"): Promise<{
    status: string;
    message: string;
    filename: string;
    processed_at: string;
    summary: {
      total_transactions: number;
      total_amount: number;
      risk_distribution: Record<string, number>;
      compliance_rate: number;
      high_risk_count: number;
      critical_count: number;
      medium_risk_count: number;
      low_risk_count: number;
    };
  }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    
    const response = await apiClient.post('/compliance/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Upload file and get PDF report directly
  uploadFileWithReport: async (file: File, userId: string = "bulk_upload"): Promise<Blob> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    
    const response = await apiClient.post('/compliance/upload-with-report', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    });
    return response.data;
  },
};

// Dashboard Stats Helper
export const getDashboardStats = async (): Promise<DashboardStats> => {
  try {
    const transactions = await transactionApi.getAll(1000, 0);
    
    const stats: DashboardStats = {
      totalTransactions: transactions.length,
      highRiskCount: 0,
      mediumRiskCount: 0,
      lowRiskCount: 0,
      complianceRate: 0,
      pendingReviews: 0,
    };

    transactions.forEach(tx => {
      const level = tx.risk_level?.toLowerCase();
      if (level === 'high' || level === 'critical') {
        stats.highRiskCount++;
        stats.pendingReviews++;
      } else if (level === 'medium') {
        stats.mediumRiskCount++;
        stats.pendingReviews++;
      } else {
        stats.lowRiskCount++;
      }
    });

    stats.complianceRate = stats.totalTransactions > 0 
      ? Math.round((stats.lowRiskCount / stats.totalTransactions) * 100) 
      : 100;

    return stats;
  } catch (error) {
    // Return default stats if API fails
    return {
      totalTransactions: 0,
      highRiskCount: 0,
      mediumRiskCount: 0,
      lowRiskCount: 0,
      complianceRate: 100,
      pendingReviews: 0,
    };
  }
};
