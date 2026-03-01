import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { 
  Upload, 
  FileText, 
  Download, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  DollarSign, 
  AlertTriangle,
  Shield,
  TrendingUp,
  FileSpreadsheet,
  File,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import { complianceApi } from '../api/transactions';

interface UploadResult {
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
}

export const BulkReports: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [downloading, setDownloading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const allowedTypes = ['.csv', '.xlsx', '.xls', '.pdf'];
      const fileExt = selectedFile.name.toLowerCase().split('.').pop();
      
      if (!fileExt || !allowedTypes.includes(`.${fileExt}`)) {
        toast.error('Invalid file type. Please upload CSV, Excel, or PDF files.');
        return;
      }
      
      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        toast.error('File too large. Maximum size is 10MB.');
        return;
      }
      
      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      const response = await complianceApi.uploadFile(file);
      setResult(response);
      toast.success(`Successfully processed ${response.summary.total_transactions} transactions!`);
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to process file');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!file) return;

    try {
      setDownloading(true);
      const blob = await complianceApi.uploadFileWithReport(file);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `compliance_report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('PDF report downloaded successfully!');
    } catch (error: any) {
      console.error('Download error:', error);
      toast.error(error.response?.data?.detail || 'Failed to download report');
    } finally {
      setDownloading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getRiskColor = (count: number) => {
    if (count === 0) return 'text-green-600';
    if (count <= 5) return 'text-amber-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Bulk Upload & Reports</h1>
          <p className="text-slate-500 mt-1">
            Upload transaction files and generate AI-powered compliance reports
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Upload className="w-5 h-5 mr-2 text-blue-600" />
              Upload Transactions
            </CardTitle>
            <CardDescription>
              Upload a CSV, Excel (.xlsx), or PDF file containing transaction data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Drop Zone */}
              <div 
                className={`
                  border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer
                  ${file 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'
                  }
                `}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls,.pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                
                {file ? (
                  <div className="flex flex-col items-center">
                    <FileText className="w-12 h-12 text-blue-600 mb-2" />
                    <p className="font-medium text-slate-900">{file.name}</p>
                    <p className="text-sm text-slate-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="mt-2 text-red-600 hover:text-red-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        clearFile();
                      }}
                    >
                      <X className="w-4 h-4 mr-1" />
                      Remove
                    </Button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <Upload className="w-12 h-12 text-slate-400 mb-2" />
                    <p className="font-medium text-slate-700">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-sm text-slate-500 mt-1">
                      CSV, Excel (.xlsx, .xls), or PDF (max 10MB)
                    </p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Button 
                  className="flex-1"
                  onClick={handleUpload}
                  disabled={!file || uploading}
                >
                  {uploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <FileSpreadsheet className="w-4 h-4 mr-2" />
                      Analyze Transactions
                    </>
                  )}
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={handleDownloadReport}
                  disabled={!file || downloading}
                >
                  {downloading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                </Button>
              </div>

              {/* Supported Formats Info */}
              <div className="p-4 bg-slate-50 rounded-lg">
                <h4 className="font-medium text-slate-700 mb-2">Supported File Formats</h4>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="flex items-center text-slate-600">
                    <FileText className="w-4 h-4 mr-1 text-blue-500" />
                    CSV
                  </div>
                  <div className="flex items-center text-slate-600">
                    <FileSpreadsheet className="w-4 h-4 mr-1 text-green-500" />
                    Excel
                  </div>
                  <div className="flex items-center text-slate-600">
                    <File className="w-4 h-4 mr-1 text-red-500" />
                    PDF
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="w-5 h-5 mr-2 text-blue-600" />
              Analysis Results
            </CardTitle>
            <CardDescription>
              View the compliance analysis summary
            </CardDescription>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-6">
                {/* Success Badge */}
                <div className="flex items-center justify-center p-4 bg-green-50 rounded-lg">
                  <CheckCircle2 className="w-6 h-6 text-green-600 mr-2" />
                  <span className="font-semibold text-green-700">Analysis Complete</span>
                </div>

                {/* Summary Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-50 rounded-lg text-center">
                    <DollarSign className="w-5 h-5 text-slate-500 mx-auto mb-1" />
                    <p className="text-2xl font-bold text-slate-900">
                      {result.summary.total_transactions}
                    </p>
                    <p className="text-sm text-slate-500">Transactions</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg text-center">
                    <TrendingUp className="w-5 h-5 text-slate-500 mx-auto mb-1" />
                    <p className="text-2xl font-bold text-slate-900">
                      ${(result.summary.total_amount / 1000).toFixed(1)}K
                    </p>
                    <p className="text-sm text-slate-500">Total Value</p>
                  </div>
                </div>

                {/* Risk Distribution */}
                <div>
                  <h4 className="font-medium text-slate-700 mb-3">Risk Distribution</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <Shield className="w-4 h-4 text-green-600 mr-2" />
                        <span className="text-slate-700">Low Risk</span>
                      </div>
                      <span className="font-semibold text-green-700">
                        {result.summary.low_risk_count}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                      <div className="flex items-center">
                        <AlertCircle className="w-4 h-4 text-amber-600 mr-2" />
                        <span className="text-slate-700">Medium Risk</span>
                      </div>
                      <span className="font-semibold text-amber-700">
                        {result.summary.medium_risk_count}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div className="flex items-center">
                        <AlertTriangle className="w-4 h-4 text-red-600 mr-2" />
                        <span className="text-slate-700">High Risk</span>
                      </div>
                      <span className={`font-semibold ${getRiskColor(result.summary.high_risk_count)}`}>
                        {result.summary.high_risk_count}
                      </span>
                    </div>
                    {result.summary.critical_count > 0 && (
                      <div className="flex items-center justify-between p-3 bg-red-100 rounded-lg">
                        <div className="flex items-center">
                          <AlertTriangle className="w-4 h-4 text-red-700 mr-2" />
                          <span className="text-slate-700 font-medium">Critical</span>
                        </div>
                        <span className="font-bold text-red-700">
                          {result.summary.critical_count}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Compliance Rate */}
                <div className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-slate-700 font-medium">Compliance Rate</span>
                    <Badge variant={result.summary.compliance_rate >= 90 ? 'success' : 'warning'}>
                      {result.summary.compliance_rate.toFixed(1)}%
                    </Badge>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        result.summary.compliance_rate >= 90 ? 'bg-green-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${result.summary.compliance_rate}%` }}
                    />
                  </div>
                </div>

                {/* Download Report Button */}
                <Button 
                  className="w-full" 
                  size="lg"
                  onClick={handleDownloadReport}
                  disabled={downloading}
                >
                  {downloading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating PDF...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Download Full PDF Report
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <FileText className="w-16 h-16 text-slate-300 mb-4" />
                <p className="text-slate-500">
                  Upload a transaction file to see analysis results
                </p>
                <p className="text-sm text-slate-400 mt-1">
                  The system will automatically analyze each transaction and generate a compliance report
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* How It Works */}
      <Card>
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Upload className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-medium text-slate-900">1. Upload File</h4>
              <p className="text-sm text-slate-500 mt-1">
                Upload CSV, Excel, or PDF bank statements
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-medium text-slate-900">2. Parse & Extract</h4>
              <p className="text-sm text-slate-500 mt-1">
                AI extracts transactions from your file
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Shield className="w-6 h-6 text-amber-600" />
              </div>
              <h4 className="font-medium text-slate-900">3. Risk Analysis</h4>
              <p className="text-sm text-slate-500 mt-1">
                Each transaction is analyzed for risk factors
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Download className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-medium text-slate-900">4. Download Report</h4>
              <p className="text-sm text-slate-500 mt-1">
                Get comprehensive PDF compliance report
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
