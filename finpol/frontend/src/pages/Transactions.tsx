import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Card, CardContent } from '../components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Select } from '../components/ui/Select';
import { Search, Plus, Filter, Download, RefreshCw, AlertTriangle, Trash2 } from 'lucide-react';
import { TransactionForm } from '../components/TransactionForm';
import { Transaction, TransactionCreate } from '../types';
import { transactionApi } from '../api/transactions';

export const Transactions: React.FC = () => {
    const navigate = useNavigate();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterRisk, setFilterRisk] = useState<string>('all');
    const [filterType, setFilterType] = useState<string>('all');

    const fetchTransactions = async () => {
        try {
            setLoading(true);
            const data = await transactionApi.getAll(100, 0);
            setTransactions(data);
        } catch (error) {
            console.error('Failed to fetch transactions:', error);
            toast.error('Failed to load transactions');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTransactions();
    }, []);

    const handleCreateTransaction = async (data: TransactionCreate) => {
        try {
            const newTransaction = await transactionApi.create(data);
            toast.success('Transaction created successfully!');
            setIsModalOpen(false);
            fetchTransactions();
            navigate(`/transactions/${newTransaction.id}`);
        } catch (error) {
            console.error('Failed to create transaction:', error);
            toast.error('Failed to create transaction');
        }
    };

    const handleDeleteTransaction = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this transaction?')) return;
        
        try {
            await transactionApi.delete(id);
            toast.success('Transaction deleted');
            fetchTransactions();
        } catch (error) {
            console.error('Failed to delete transaction:', error);
            toast.error('Failed to delete transaction');
        }
    };

    const filteredTxns = transactions.filter(txn => {
        const matchesSearch = 
            txn.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            txn.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            txn.amount.toString().includes(searchTerm);
        
        const matchesRisk = filterRisk === 'all' || 
            (filterRisk === 'high' && (txn.risk_level === 'High' || txn.risk_level === 'Critical')) ||
            (filterRisk === 'medium' && txn.risk_level === 'Medium') ||
            (filterRisk === 'low' && txn.risk_level === 'Low');
        
        const matchesType = filterType === 'all' || txn.transaction_type === filterType;
        
        return matchesSearch && matchesRisk && matchesType;
    });

    const getRiskBadgeVariant = (level: string | undefined) => {
        switch (level?.toLowerCase()) {
            case 'low': return 'success';
            case 'medium': return 'warning';
            case 'high':
            case 'critical': return 'destructive';
            default: return 'secondary';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-slate-500">Loading transactions...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Transactions</h1>
                    <p className="text-slate-500 mt-1">Manage and analyze all transactions across the system.</p>
                </div>
                <div className="flex items-center space-x-3">
                    <Button variant="outline" onClick={fetchTransactions} className="hidden sm:flex items-center">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                    <Button variant="outline" className="hidden sm:flex items-center">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                    </Button>
                    <Button onClick={() => setIsModalOpen(true)} className="flex items-center">
                        <Plus className="w-4 h-4 mr-2" />
                        New Transaction
                    </Button>
                </div>
            </div>

            <Card>
                <CardContent className="p-0">
                    <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row gap-4 justify-between items-center bg-white rounded-t-xl">
                        <div className="relative w-full sm:w-96">
                            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                            <Input
                                className="pl-9"
                                placeholder="Search by ID, User, or Amount..."
                                value={searchTerm}
                                onChange={e => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="flex gap-2 w-full sm:w-auto">
                            <Select 
                                value={filterRisk} 
                                onChange={e => setFilterRisk(e.target.value)}
                                className="w-full sm:w-32"
                            >
                                <option value="all">All Risk</option>
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </Select>
                            <Select 
                                value={filterType} 
                                onChange={e => setFilterType(e.target.value)}
                                className="w-full sm:w-32"
                            >
                                <option value="all">All Types</option>
                                <option value="transfer">Transfer</option>
                                <option value="payment">Payment</option>
                                <option value="withdrawal">Withdrawal</option>
                                <option value="deposit">Deposit</option>
                            </Select>
                        </div>
                    </div>

                    {filteredTxns.length === 0 ? (
                        <div className="text-center py-12">
                            <AlertTriangle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                            <p className="text-slate-500">
                                {transactions.length === 0 
                                    ? "No transactions yet. Create your first transaction to get started."
                                    : "No transactions match your filters."
                                }
                            </p>
                            {transactions.length === 0 && (
                                <Button className="mt-4" onClick={() => setIsModalOpen(true)}>
                                    Create Transaction
                                </Button>
                            )}
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Transaction ID</TableHead>
                                    <TableHead>User</TableHead>
                                    <TableHead>Amount</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>Country</TableHead>
                                    <TableHead>Risk Score</TableHead>
                                    <TableHead>Risk Level</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredTxns.map((txn) => (
                                    <TableRow
                                        key={txn.id}
                                        className="cursor-pointer hover:bg-slate-50"
                                        onClick={() => navigate(`/transactions/${txn.id}`)}
                                    >
                                        <TableCell className="font-medium text-blue-600">{txn.id}</TableCell>
                                        <TableCell>{txn.user_id}</TableCell>
                                        <TableCell className="font-medium">
                                            {new Intl.NumberFormat('en-US', { style: 'currency', currency: txn.currency }).format(txn.amount)}
                                        </TableCell>
                                        <TableCell className="capitalize">{txn.transaction_type}</TableCell>
                                        <TableCell>{txn.country}</TableCell>
                                        <TableCell>
                                            <span className={
                                                (txn.risk_score ?? 0) > 80 ? 'text-red-600 font-bold' :
                                                (txn.risk_score ?? 0) > 40 ? 'text-amber-600 font-bold' : 'text-green-600 font-medium'
                                            }>
                                                {txn.risk_score ?? 'N/A'}/100
                                            </span>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={getRiskBadgeVariant(txn.risk_level)}>
                                                {txn.risk_level || 'Unknown'}
                                            </Badge>
                                        </TableCell>
                                        <TableCell onClick={(e) => e.stopPropagation()}>
                                            <Button 
                                                variant="ghost" 
                                                size="icon"
                                                className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                                onClick={(e) => handleDeleteTransaction(txn.id, e)}
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}

                    <div className="p-4 border-t border-slate-200 flex items-center justify-between bg-slate-50 rounded-b-xl">
                        <span className="text-sm text-slate-500">Showing {filteredTxns.length} of {transactions.length} results</span>
                        <div className="flex space-x-2">
                            <Button variant="outline" size="sm" disabled>Previous</Button>
                            <Button variant="outline" size="sm">Next</Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title="Create New Transaction"
                className="max-w-2xl"
            >
                <TransactionForm
                    onCancel={() => setIsModalOpen(false)}
                    onSubmit={handleCreateTransaction}
                />
            </Modal>
        </div>
    );
};
