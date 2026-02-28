import { useState } from 'react'

interface TransactionFormProps {
  onSubmit: (data: any) => void
}

function TransactionForm({ onSubmit }: TransactionFormProps) {
  const [formData, setFormData] = useState({
    user_id: '',
    amount: '',
    currency: 'USD',
    transaction_type: 'transfer',
    recipient_account: '',
    sender_account: '',
    description: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount)
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            User ID
          </label>
          <input
            type="text"
            name="user_id"
            value={formData.user_id}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount
          </label>
          <input
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            required
            min="0"
            step="0.01"
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Currency
          </label>
          <select
            name="currency"
            value={formData.currency}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
            <option value="INR">INR</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Transaction Type
          </label>
          <select
            name="transaction_type"
            value={formData.transaction_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="transfer">Transfer</option>
            <option value="payment">Payment</option>
            <option value="withdrawal">Withdrawal</option>
            <option value="deposit">Deposit</option>
            <option value="investment">Investment</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sender Account
          </label>
          <input
            type="text"
            name="sender_account"
            value={formData.sender_account}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Recipient Account
          </label>
          <input
            type="text"
            name="recipient_account"
            value={formData.recipient_account}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <button
        type="submit"
        className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700"
      >
        Submit Transaction
      </button>
    </form>
  )
}

export default TransactionForm
