import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Activity, ShieldAlert, CheckCircle2, Clock, RefreshCw, AlertTriangle, DollarSign, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Transaction, DashboardStats, RISK_LEVELS } from '../types';
import { transactionApi, getDashboardStats } from '../api/transactions';

const CHART_COLORS = {
  low: '#22c55e',
  medium: '#eab308',
  high: '#ef4444',
  critical: '#dc2626',
};

const volumeData = [
  { name: 'Mon', count: 0 },
  { name: 'Tue', count: 0 },
  { name: 'Wed', count: 0 },
  { name: 'Thu', count: 0 },
  { name: 'Fri', count: 0 },
  { name: 'Sat', count: 0 },
  { name: 'Sun', count: 0 }
];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    totalTransactions: 0,
    highRiskCount: 0,
    mediumRiskCount: 0,
    lowRiskCount: 0,
    complianceRate: 100,
    pendingReviews: 0,
  });
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [txns, dashboardStats] = await Promise.all([
        transactionApi.getAll(5, 0),
        getDashboardStats(),
      ]);
      setTransactions(txns);
      setStats(dashboardStats);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const riskData = [
    { name: 'Low Risk', value: stats.lowRiskCount, color: CHART_COLORS.low },
    { name: 'Medium Risk', value: stats.mediumRiskCount, color: CHART_COLORS.medium },
    { name: 'High Risk', value: stats.highRiskCount, color: CHART_COLORS.high },
  ].filter(d => d.value > 0);

  // Ensure at least one entry for pie chart
  if (riskData.length === 0) {
    riskData.push({ name: 'No Data', value: 1, color: '#e2e8f0' });
  }

  const statCards = [
    { 
      title: "Total Transactions", 
      value: stats.totalTransactions.toLocaleString(), 
      change: "+12.5%", 
      isPositive: true, 
      icon: Activity, 
      color: "text-blue-600", 
      bg: "bg-blue-100" 
    },
    { 
      title: "High Risk", 
      value: stats.highRiskCount.toString(), 
      change: stats.highRiskCount > 0 ? "+Alert" : "0", 
      isPositive: stats.highRiskCount === 0, 
      icon: ShieldAlert, 
      color: stats.highRiskCount > 0 ? "text-red-600" : "text-green-600", 
      bg: stats.highRiskCount > 0 ? "bg-red-100" : "bg-green-100" 
    },
    { 
      title: "Compliance Rate", 
      value: `${stats.complianceRate}%`, 
      change: stats.complianceRate >= 95 ? "+Good" : "-Warning", 
      isPositive: stats.complianceRate >= 95, 
      icon: CheckCircle2, 
      color: stats.complianceRate >= 95 ? "text-green-600" : "text-amber-600", 
      bg: stats.complianceRate >= 95 ? "bg-green-100" : "bg-amber-100" 
    },
    { 
      title: "Pending Reviews", 
      value: stats.pendingReviews.toString(), 
      change: stats.pendingReviews > 0 ? "Action Required" : "All Clear", 
      isPositive: stats.pendingReviews === 0, 
      icon: Clock, 
      color: stats.pendingReviews === 0 ? "text-slate-600" : "text-amber-600", 
      bg: stats.pendingReviews === 0 ? "bg-slate-100" : "bg-amber-100" 
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Payment Gateway Dashboard</h1>
          <p className="text-slate-500 mt-1">Real-time transaction monitoring and compliance overview.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-lg">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-sm font-medium text-green-700">System Online</span>
          </div>
          <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <Card key={stat.title} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                  <p className="text-2xl font-bold text-slate-900 mt-2">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${stat.bg}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm">
                <span className={`inline-flex items-center font-medium ${stat.isPositive ? 'text-green-600' : stat.title === 'High Risk' ? 'text-red-600' : 'text-amber-600'}`}>
                  {stat.isPositive ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <AlertTriangle className="w-4 h-4 mr-1" />}
                  {stat.change}
                </span>
                <span className="text-slate-500 ml-2">vs last week</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg font-semibold">Transaction Volume (This Week)</CardTitle>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <TrendingUp className="w-4 h-4" />
              <span>{stats.totalTransactions} total</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={volumeData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold">Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full flex flex-col items-center justify-center">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    itemStyle={{ color: '#0f172a' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-2 w-full flex-wrap">
                {riskData.filter(d => d.name !== 'No Data').map(item => (
                  <div key={item.name} className="flex items-center text-xs text-slate-600">
                    <span className="w-3 h-3 rounded-full mr-1.5" style={{ backgroundColor: item.color }}></span>
                    {item.name}: {item.value}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg font-semibold">Recent Transactions</CardTitle>
          <Button variant="outline" size="sm" onClick={() => navigate('/transactions')}>
            View All
          </Button>
        </CardHeader>
        <CardContent>
          {transactions.length === 0 ? (
            <div className="text-center py-12">
              <DollarSign className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500">No transactions yet. Create your first transaction to get started.</p>
              <Button className="mt-4" onClick={() => navigate('/transactions')}>
                Go to Transactions
              </Button>
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
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((txn) => (
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
                      <Badge variant={
                        txn.risk_level === 'Low' ? 'success' :
                        txn.risk_level === 'Medium' ? 'warning' : 'destructive'
                      }>
                        {txn.risk_level || 'Unknown'}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
