import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Search, BookOpen, AlertTriangle, FileText, ChevronRight, RefreshCw, Loader2, Sparkles } from 'lucide-react';
import { Regulation } from '../types';
import { complianceApi } from '../api/transactions';

const regulationCategories = [
  { value: 'all', label: 'All Categories' },
  { value: 'aml', label: 'Anti-Money Laundering' },
  { value: 'kyc', label: 'Know Your Customer' },
  { value: 'international', label: 'International Sanctions' },
  { value: 'reporting', label: 'Reporting Requirements' },
  { value: 'european', label: 'European Regulations' },
];

export const Compliance: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [generateTxId, setGenerateTxId] = useState('');
  const [generating, setGenerating] = useState(false);

  const fetchRegulations = async () => {
    try {
      setLoading(true);
      const data = await complianceApi.getRegulations();
      setRegulations(data);
    } catch (error) {
      console.error('Failed to fetch regulations:', error);
      toast.error('Failed to load regulations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRegulations();
  }, []);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      fetchRegulations();
      return;
    }

    try {
      setSearching(true);
      const results = await complianceApi.searchRegulations(searchTerm);
      setRegulations(results);
    } catch (error) {
      console.error('Failed to search regulations:', error);
      toast.error('Search failed');
    } finally {
      setSearching(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!generateTxId.trim()) {
      toast.error('Please enter a transaction ID');
      return;
    }

    try {
      setGenerating(true);
      const report = await complianceApi.generateReport(generateTxId, 50, 'Medium');
      toast.success('Report generated successfully');
      console.log('Generated report:', report);
    } catch (error) {
      console.error('Failed to generate report:', error);
      toast.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const filteredRegs = regulations.filter(reg => {
    if (selectedCategory === 'all') return true;
    const category = reg.category?.toLowerCase() || '';
    return category.includes(selectedCategory);
  });

  const getCategoryColor = (category?: string) => {
    switch (category?.toLowerCase()) {
      case 'aml':
      case 'general':
        return 'bg-red-100 text-red-700';
      case 'kyc':
      case 'identity':
        return 'bg-blue-100 text-blue-700';
      case 'international':
        return 'bg-purple-100 text-purple-700';
      case 'reporting':
        return 'bg-amber-100 text-amber-700';
      case 'european':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
          <p className="text-slate-500">Loading compliance data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Compliance & Regulations</h1>
          <p className="text-slate-500 mt-1">Review regulatory requirements and search the AI-powered compliance database.</p>
        </div>
        <Button variant="outline" onClick={fetchRegulations} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <BookOpen className="w-5 h-5 mr-2 text-blue-600" />
              Regulations Database
              <Badge variant="secondary" className="ml-2">{filteredRegs.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <Input
                  className="pl-9 bg-slate-50"
                  placeholder="Search regulations by keyword..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
              <Button onClick={handleSearch} disabled={searching}>
                {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
              </Button>
              <Select 
                value={selectedCategory} 
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full sm:w-48"
              >
                {regulationCategories.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </Select>
            </div>

            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              {filteredRegs.length === 0 ? (
                <div className="text-center py-12 text-slate-500">
                  <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                  <p>No regulations found</p>
                  <Button variant="link" onClick={() => { setSearchTerm(''); fetchRegulations(); }}>
                    Clear filters
                  </Button>
                </div>
              ) : (
                filteredRegs.map((reg, index) => (
                  <div 
                    key={reg.id || index} 
                    className="p-4 border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50/50 transition-colors group cursor-pointer"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-xs font-bold text-blue-600">{reg.id || `REG-${index + 1}`}</span>
                          {reg.category && (
                            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${getCategoryColor(reg.category)}`}>
                              {reg.category}
                            </span>
                          )}
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900">{reg.title || `Regulation ${index + 1}`}</h3>
                        <p className="text-sm text-slate-600 mt-2 leading-relaxed">{reg.content}</p>
                        {reg.source && (
                          <p className="text-xs text-slate-400 mt-2">Source: {reg.source}</p>
                        )}
                      </div>
                      <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2">
                        <ChevronRight className="w-5 h-5 text-blue-600" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-blue-600" />
                  AI Compliance Reports
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-slate-600">
                  Generate AI-powered compliance analysis for any transaction using our RAG-powered system.
                </p>
                <div className="flex space-x-2">
                  <Input 
                    placeholder="Enter TXN ID..." 
                    value={generateTxId}
                    onChange={(e) => setGenerateTxId(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleGenerateReport} 
                    disabled={generating}
                    className="shrink-0"
                  >
                    {generating ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white border-none shadow-md">
            <CardContent className="p-6">
              <div className="flex items-center mb-3">
                <Sparkles className="w-5 h-5 mr-2" />
                <h3 className="font-semibold text-lg">AI-Powered Search</h3>
              </div>
              <p className="text-blue-100 text-sm mb-4">
                Our RAG system uses AI to find the most relevant regulations based on your transaction context.
              </p>
              <div className="space-y-2 text-sm text-blue-100">
                <div className="flex items-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-200 mr-2"></span>
                  Semantic search across regulations
                </div>
                <div className="flex items-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-200 mr-2"></span>
                  Context-aware recommendations
                </div>
                <div className="flex items-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-200 mr-2"></span>
                  Real-time compliance updates
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-amber-600" />
                Quick Stats
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">Total Regulations</span>
                  <span className="font-semibold text-slate-900">{regulations.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">AML Rules</span>
                  <Badge variant="destructive">Active</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">KYC Compliance</span>
                  <Badge variant="success">Active</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">RAG System</span>
                  <Badge variant="success">Online</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
