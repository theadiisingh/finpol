import { useState, useEffect } from 'react'
import TransactionForm from '../components/TransactionForm'
import RiskBadge from '../components/RiskBadge'
import { transactionApi } from '../services/api'

interface Transaction {
  id: string
  user_id: string
  amount: number
  currency: string
  transaction_type: string
  status: string
  risk_score?: number
}

function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadTransactions()
  }, [])

  const loadTransactions = async () => {
    setLoading(true)
    try {
      const res = await transactionApi.getAll()
      setTransactions(res.data)
    } catch (error) {
      console.error('Failed to load transactions')
    }
    setLoading(false)
  }

  const handleSubmit = async (data: any) => {
    try {
      await transactionApi.create(data)
      setShowForm(false)
      loadTransactions()
    } catch (error) {
      console.error('Failed to create transaction')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          {showForm ? 'Cancel' : 'New Transaction'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Create Transaction</h2>
          <TransactionForm onSubmit={handleSubmit} />
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {transactions.map((tx) => (
              <tr key={tx.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{tx.id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {tx.currency} {tx.amount.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{tx.transaction_type}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${
                    tx.status === 'approved' ? 'bg-green-100 text-green-800' :
                    tx.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {tx.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <RiskBadge score={tx.risk_score || 0} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Transactions
