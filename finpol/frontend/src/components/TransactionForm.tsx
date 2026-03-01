import React, { useState } from 'react';
import { toast } from 'sonner';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Button } from './ui/Button';
import { TransactionCreate, COUNTRIES, MERCHANT_TYPES, CURRENCIES } from '../types';

interface TransactionFormProps {
  onSubmit: (data: TransactionCreate) => void;
  onCancel: () => void;
}

export const TransactionForm: React.FC<TransactionFormProps> = ({ onSubmit, onCancel }) => {
    const [loading, setLoading] = useState(false);
    const [riskScore, setRiskScore] = useState(0.2);
    const [formData, setFormData] = useState({
        user_id: '',
        amount: '',
        currency: 'USD',
        transaction_type: 'transfer' as const,
        description: '',
        sender_account: '',
        recipient_account: '',
        country: 'US',
        merchant_type: 'retail',
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const data: TransactionCreate = {
                user_id: formData.user_id,
                amount: parseFloat(formData.amount),
                currency: formData.currency,
                transaction_type: formData.transaction_type,
                description: formData.description || undefined,
                sender_account: formData.sender_account,
                recipient_account: formData.recipient_account,
                country: formData.country,
                merchant_type: formData.merchant_type,
                device_risk_score: riskScore,
            };
            
            onSubmit(data);
        } catch (error) {
            console.error('Error submitting form:', error);
            toast.error('Failed to submit transaction');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">User ID *</label>
                    <Input 
                        placeholder="USR-12345" 
                        required 
                        value={formData.user_id}
                        onChange={(e) => handleChange('user_id', e.target.value)}
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Amount *</label>
                    <Input 
                        type="number" 
                        step="0.01" 
                        placeholder="0.00" 
                        required
                        value={formData.amount}
                        onChange={(e) => handleChange('amount', e.target.value)}
                    />
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Currency *</label>
                    <Select 
                        required
                        value={formData.currency}
                        onChange={(e) => handleChange('currency', e.target.value)}
                    >
                        {CURRENCIES.map(c => (
                            <option key={c.code} value={c.code}>{c.code} - {c.name}</option>
                        ))}
                    </Select>
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Transaction Type *</label>
                    <Select 
                        required
                        value={formData.transaction_type}
                        onChange={(e) => handleChange('transaction_type', e.target.value)}
                    >
                        <option value="transfer">Transfer</option>
                        <option value="payment">Payment</option>
                        <option value="withdrawal">Withdrawal</option>
                        <option value="deposit">Deposit</option>
                    </Select>
                </div>
            </div>

            <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Description</label>
                <Input 
                    placeholder="Transaction description..." 
                    value={formData.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Sender Account *</label>
                    <Input 
                        placeholder="ACC-XXX" 
                        required
                        value={formData.sender_account}
                        onChange={(e) => handleChange('sender_account', e.target.value)}
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Recipient Account *</label>
                    <Input 
                        placeholder="ACC-YYY" 
                        required
                        value={formData.recipient_account}
                        onChange={(e) => handleChange('recipient_account', e.target.value)}
                    />
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Country *</label>
                    <Select 
                        required
                        value={formData.country}
                        onChange={(e) => handleChange('country', e.target.value)}
                    >
                        {COUNTRIES.map(c => (
                            <option key={c.code} value={c.code}>{c.name}</option>
                        ))}
                    </Select>
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Merchant Type</label>
                    <Select 
                        value={formData.merchant_type}
                        onChange={(e) => handleChange('merchant_type', e.target.value)}
                    >
                        {MERCHANT_TYPES.map(m => (
                            <option key={m.value} value={m.value}>{m.label}</option>
                        ))}
                    </Select>
                </div>
            </div>

            <div className="space-y-2">
                <label className="flex justify-between text-sm font-medium text-slate-700">
                    <span>Device Risk Score</span>
                    <span className="text-blue-600 font-bold">{riskScore.toFixed(1)}</span>
                </label>
                <input
                    type="range"
                    min="0" max="1" step="0.1"
                    className="w-full accent-blue-600 cursor-pointer"
                    value={riskScore}
                    onChange={(e) => setRiskScore(parseFloat(e.target.value))}
                />
                <p className="text-xs text-slate-500">A higher score implies an unfamiliar or compromised device.</p>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-slate-100">
                <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
                <Button type="submit" disabled={loading}>
                    {loading ? 'Processing...' : 'Create Transaction'}
                </Button>
            </div>
        </form>
    );
};
