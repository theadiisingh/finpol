import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { ArrowLeft, ShieldAlert, CheckCircle, Flag, Trash2, ShieldCheck, RefreshCw, Loader2 } from 'lucide-react';
import { Transaction, RiskResponse, ComplianceReport } from '../types';
import { transactionApi, complianceApi } from '../api/transactions';

export const TransactionDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    
    const [transaction, setTransaction] = useState<Transaction | null>(null);
    const [riskResponse, setRiskResponse] = useState<RiskResponse | null>(null);
    const [complianceReport, setComplianceReport] = useState<ComplianceReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<string | null>(null);

    useEffect(() => {
        const fetchTransaction = async () => {
            if (!id) return;
            
            try {
                setLoading(true);
                const txn = await transactionApi.getById(id);
                setTransaction(txn);
                
                // If transaction has risk score, get compliance report
                if (txn.risk_score !== undefined && txn.risk_level) {
                    try {
                        const report = await complianceApi.generateReport(
                            id, 
                            txn.risk_score, 
                            txn.risk_level
                        );
                        setComplianceReport(report);
                    } catch (err) {
                        console.error('Failed to fetch compliance report:', err);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch transaction:', error);
                toast.error('Transaction not found');
                navigate('/transactions');
            } finally {
                setLoading(false);
            }
        };

        fetchTransaction();
    }, [id, navigate]);

    const handleApprove = async () => {
        setActionLoading('approve');
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        toast.success('Transaction approved and funds released.');
        setActionLoading(null);
    };

    const handleFlag = async () => {
        setActionLoading('flag');
        await new Promise(resolve => setTimeout(resolve, 1000));
        toast.warning('Transaction flagged for manual compliance review.');
        setActionLoading(null);
    };

    const handleDelete = async () => {
        if (!confirm('Are you sure you want to delete this transaction?')) return;
        
        setActionLoading('delete');
        try {
            await transactionApi.delete(id!);
            toast.success('Transaction deleted successfully');
            navigate('/transactions');
        } catch (error) {
            toast.error('Failed to delete transaction');
        } finally {
            setActionLoading(null);
        }
    };

    const handleReanalyze = async () => {
        if (!transaction) return;
        
        setLoading(true);
        try {
            const analysis = await transactionApi.analyze({
                transaction_id: transaction.id,
                user_id: transaction.user_id,
                amount: transaction.amount,
                currency: transaction.currency,
                transaction_type: transaction.transaction_type,
                country: transaction.country,
                merchant_type: transaction.merchant_type,
                device_risk_score: transaction.device_risk_score,
            });
            setRiskResponse(analysis);
            
            // Refresh transaction data
            const updated = await transactionApi.getById(id!);
            setTransaction(updated);
            
            toast.success('Transaction re-analyzed successfully');
        } catch (error) {
            toast.error('Failed to re-analyze transaction');
        } finally {
            setLoading(false);
        }
    };

    if (loading && !transaction) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
                    <p className="text-slate-500">Loading transaction details...</p>
                </div>
            </div>
        );
    }

    if (!transaction) {
        return (
            <div className="flex flex-col items-center justify-center h-96">
                <ShieldAlert className="w-16 h-16 text-slate-300 mb-4" />
                <p className="text-slate-500">Transaction not found</p>
                <Button className="mt-4" onClick={() => navigate('/transactions')}>
                    Back to Transactions
                </Button>
            </div>
        );
    }

    const isHighRisk = transaction.risk_level === 'High' || transaction.risk_level === 'Critical';
    const isMediumRisk = transaction.risk_level === 'Medium';
    
    const getRiskColor = () => {
        if (isHighRisk) return '#ef4444';
        if (isMediumRisk) return '#eab308';
        return '#22c55e';
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => navigate('/transactions')}
                        className="p-2 bg-white rounded-full shadow-sm hover:bg-slate-50 transition-colors text-slate-600"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <div className="flex items-center space-x-3">
                            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Transaction {transaction.id}</h1>
                            <Badge variant={
                                transaction.risk_level === 'Low' ? 'success' : 
                                isHighRisk ? 'destructive' : 'warning'
                            }>
                                {transaction.risk_level || 'Unknown'} Risk
                            </Badge>
                        </div>
                        <p className="text-slate-500 mt-1">
                            Processed on {new Date(transaction.timestamp).toLocaleString()}
                        </p>
                    </div>
                </div>
                <Button variant="outline" onClick={handleReanalyze} disabled={loading}>
                    <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Re-analyze
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Transaction Details</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-y-6 gap-x-8">
                                <div>
                                    <p className="text-sm font-medium text-slate-500">User ID</p>
                                    <p className="text-base font-semibold text-slate-900 mt-1">{transaction.user_id}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Amount</p>
                                    <p className="text-xl font-bold text-blue-600 mt-1">
                                        {new Intl.NumberFormat('en-US', { 
                                            style: 'currency', 
                                            currency: transaction.currency 
                                        }).format(transaction.amount)}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Type</p>
                                    <p className="text-base font-medium text-slate-900 mt-1 capitalize">
                                        {transaction.transaction_type}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Description</p>
                                    <p className="text-base text-slate-700 mt-1">
                                        {transaction.description || 'N/A'}
                                    </p>
                                </div>
                                <div className="col-span-2 h-px bg-slate-100 my-2"></div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Sender Account</p>
                                    <p className="text-base font-mono text-slate-700 mt-1">
                                        {transaction.sender_account || 'N/A'}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Recipient Account</p>
                                    <p className="text-base font-mono text-slate-700 mt-1">
                                        {transaction.recipient_account || 'N/A'}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Country</p>
                                    <p className="text-base font-medium text-slate-900 mt-1">{transaction.country}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Merchant Type</p>
                                    <p className="text-base text-slate-900 mt-1 capitalize">{transaction.merchant_type}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Device Risk Score</p>
                                    <p className="text-base font-medium text-slate-900 mt-1">
                                        {transaction.device_risk_score?.toFixed(2) || '0.00'}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Currency</p>
                                    <p className="text-base font-medium text-slate-900 mt-1">{transaction.currency}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center space-x-2">
                            <ShieldCheck className="w-5 h-5 text-blue-600" />
                            <CardTitle>AI Compliance Analysis</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {complianceReport?.llm_analysis ? (
                                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 leading-relaxed text-slate-700">
                                    {complianceReport.llm_analysis}
                                </div>
                            ) : (
                                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 leading-relaxed text-slate-700">
                                    {riskResponse?.compliance_explanation || 
                                        "Compliance analysis is being processed. This may take a moment for transactions with higher risk scores."}
                                </div>
                            )}
                            
                            {complianceReport?.recommendations && complianceReport.recommendations.length > 0 && (
                                <div className="mt-4">
                                    <h4 className="text-sm font-semibold text-slate-700 mb-2">Recommendations:</h4>
                                    <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                        {complianceReport.recommendations.map((rec, idx) => (
                                            <li key={idx}>{rec}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                <div className="space-y-6">
                    <Card className={isHighRisk ? 'border-red-200' : 'border-slate-200'}>
                        <CardHeader className={`rounded-t-xl ${isHighRisk ? 'bg-red-50/50' : isMediumRisk ? 'bg-amber-50/50' : 'bg-slate-50/50'}`}>
                            <CardTitle className="flex items-center justify-between">
                                <span>Risk Assessment</span>
                                {isHighRisk ? <ShieldAlert className="w-5 h-5 text-red-500" /> : 
                                 isMediumRisk ? <Flag className="w-5 h-5 text-amber-500" /> :
                                 <CheckCircle className="w-5 h-5 text-green-500" />}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-6 pt-6">
                            <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-200 rounded-full w-48 h-48 mx-auto relative">
                                <span className="text-5xl font-bold tracking-tighter" style={{ color: getRiskColor() }}>
                                    {transaction.risk_score ?? 'N/A'}
                                </span>
                                <span className="text-sm font-medium text-slate-500 mt-1">Out of 100</span>
                            </div>

                            <div className="mt-8 space-y-4">
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-slate-600">Decision</span>
                                    <Badge variant={
                                        transaction.risk_level === 'Low' ? 'success' : 'destructive'
                                    } className="text-sm px-3 py-1">
                                        {transaction.risk_level === 'Low' ? 'Approve' : 'Review Required'}
                                    </Badge>
                                </div>
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-slate-600">Manual Review</span>
                                    <span className="font-semibold text-slate-900">
                                        {isHighRisk || isMediumRisk ? 'Required' : 'Not Required'}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-slate-600">Device Risk</span>
                                    <span className="font-semibold text-slate-900">
                                        {(transaction.device_risk_score ?? 0).toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Actions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <Button
                                onClick={handleApprove}
                                disabled={actionLoading !== null}
                                className="w-full justify-center bg-green-600 hover:bg-green-700"
                            >
                                {actionLoading === 'approve' ? (
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                )}
                                Approve Transaction
                            </Button>
                            <Button
                                onClick={handleFlag}
                                disabled={actionLoading !== null}
                                variant="outline" 
                                className="w-full justify-center text-amber-600 hover:text-amber-700 hover:bg-amber-50 border-amber-200"
                            >
                                {actionLoading === 'flag' ? (
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <Flag className="w-4 h-4 mr-2" />
                                )}
                                Flag for Review
                            </Button>
                            <Button
                                onClick={handleDelete}
                                disabled={actionLoading !== null}
                                variant="destructive" 
                                className="w-full justify-center"
                            >
                                {actionLoading === 'delete' ? (
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <Trash2 className="w-4 h-4 mr-2" />
                                )}
                                Delete Record
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};
