import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, CheckCircle, Activity } from 'lucide-react'
import { healthApi } from '../services/api'

function Dashboard() {
  const [stats, setStats] = useState({
    totalTransactions: 1247,
    flaggedTransactions: 23,
    compliantTransactions: 1198,
    riskScore: 72
  })
  const [health, setHealth] = useState<{ status: string } | null>(null)

  useEffect(() => {
    healthApi.check()
      .then(res => setHealth(res.data))
      .catch(() => setHealth({ status: 'unhealthy' }))
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Transactions</p>
              <p className="text-2xl font-bold">{stats.totalTransactions}</p>
            </div>
            <Activity className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Flagged</p>
              <p className="text-2xl font-bold text-red-600">{stats.flaggedTransactions}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Compliant</p>
              <p className="text-2xl font-bold text-green-600">{stats.compliantTransactions}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Risk Score</p>
              <p className="text-2xl font-bold">{stats.riskScore}%</p>
            </div>
            <Shield className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        <div className="flex items-center gap-2">
          <span className={`w-3 h-3 rounded-full ${health?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span className="text-gray-700">
            API Status: {health?.status || 'Checking...'}
          </span>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b">
              <span className="text-gray-600">Transaction #{1000 + i}</span>
              <span className="text-sm text-gray-500">Risk: {i * 10 + 20}%</span>
              <span className={`px-2 py-1 rounded text-xs ${i < 2 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {i < 2 ? 'Approved' : 'Review'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
