export interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  currency: string;
  transaction_type: TransactionType;
  description?: string;
  recipient_account: string;
  sender_account: string;
  country: string;
  merchant_type: string;
  device_risk_score: number;
  timestamp: string;
  risk_score?: number;
  risk_level?: string;
}

export type TransactionType = 'transfer' | 'payment' | 'withdrawal' | 'deposit';

export interface TransactionCreate {
  user_id: string;
  amount: number;
  currency: string;
  transaction_type: TransactionType;
  description?: string;
  recipient_account: string;
  sender_account: string;
  country: string;
  merchant_type: string;
  device_risk_score: number;
}

export interface RiskResponse {
  transaction_id: string;
  risk_score: number;
  risk_level: string;
  should_approve: boolean;
  requires_review: boolean;
  compliance_explanation?: string;
}

export interface Regulation {
  id: string;
  title: string;
  content: string;
  category?: string;
  source?: string;
}

export interface ComplianceReport {
  transaction_id: string;
  compliance_status: string;
  regulations_applied: string[];
  violations: string[];
  recommendations: string[];
  llm_analysis: string;
  timestamp: string;
}

export interface DashboardStats {
  totalTransactions: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
  complianceRate: number;
  pendingReviews: number;
}

export interface RiskLevel {
  label: string;
  value: string;
  color: string;
  bgColor: string;
}

export const RISK_LEVELS: Record<string, RiskLevel> = {
  Low: { label: 'Low', value: 'Low', color: 'text-green-600', bgColor: 'bg-green-100' },
  Medium: { label: 'Medium', value: 'Medium', color: 'text-amber-600', bgColor: 'bg-amber-100' },
  High: { label: 'High', value: 'High', color: 'text-orange-600', bgColor: 'bg-orange-100' },
  Critical: { label: 'Critical', value: 'Critical', color: 'text-red-600', bgColor: 'bg-red-100' },
};

export const COUNTRIES = [
  { code: 'US', name: 'United States' },
  { code: 'UK', name: 'United Kingdom' },
  { code: 'IN', name: 'India' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'JP', name: 'Japan' },
  { code: 'CN', name: 'China' },
  { code: 'RU', name: 'Russia' },
  { code: 'KP', name: 'North Korea' },
  { code: 'IR', name: 'Iran' },
  { code: 'SY', name: 'Syria' },
  { code: 'IQ', name: 'Iraq' },
];

export const MERCHANT_TYPES = [
  { value: 'retail', label: 'Retail' },
  { value: 'crypto_exchange', label: 'Crypto Exchange' },
  { value: 'gambling', label: 'Gambling' },
  { value: 'gaming', label: 'Gaming' },
  { value: 'banking', label: 'Banking' },
  { value: 'investment', label: 'Investment' },
  { value: 'ecommerce', label: 'E-Commerce' },
  { value: 'remittance', label: 'Remittance' },
];

export const CURRENCIES = [
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'GBP', name: 'British Pound', symbol: '£' },
  { code: 'INR', name: 'Indian Rupee', symbol: '₹' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
];
