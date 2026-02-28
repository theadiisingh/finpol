import { useState, useEffect } from 'react'
import ComplianceCard from '../components/ComplianceCard'
import { complianceApi } from '../services/api'

interface Regulation {
  id: string
  title: string
  content: string
  type: string
}

function ComplianceView() {
  const [regulations, setRegulations] = useState<Regulation[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadRegulations()
  }, [])

  const loadRegulations = async () => {
    setLoading(true)
    try {
      const res = await complianceApi.getRegulations()
      setRegulations(res.data)
    } catch (error) {
      console.error('Failed to load regulations')
    }
    setLoading(false)
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadRegulations()
      return
    }
    setLoading(true)
    try {
      const res = await complianceApi.searchRegulations(searchQuery)
      setRegulations(res.data)
    } catch (error) {
      console.error('Search failed')
    }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Compliance & Regulations</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex gap-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search regulations..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={handleSearch}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
          >
            Search
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {regulations.map((reg) => (
          <ComplianceCard key={reg.id} regulation={reg} />
        ))}
      </div>

      {regulations.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          No regulations found
        </div>
      )}
    </div>
  )
}

export default ComplianceView
