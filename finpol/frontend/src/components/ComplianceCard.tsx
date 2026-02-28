import { FileText } from 'lucide-react'

interface Regulation {
  id: string
  title: string
  content: string
  type: string
}

interface ComplianceCardProps {
  regulation: Regulation
}

function ComplianceCard({ regulation }: ComplianceCardProps) {
  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      AML: 'bg-red-100 text-red-800',
      KYC: 'bg-blue-100 text-blue-800',
      GDPR: 'bg-purple-100 text-purple-800',
      SEC: 'bg-yellow-100 text-yellow-800',
      FATF: 'bg-green-100 text-green-800'
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <FileText className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">{regulation.title}</h3>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${getTypeColor(regulation.type)}`}>
          {regulation.type}
        </span>
      </div>
      <p className="mt-3 text-sm text-gray-600">{regulation.content}</p>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-xs text-gray-500">ID: {regulation.id}</span>
        <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
          View Details
        </button>
      </div>
    </div>
  )
}

export default ComplianceCard
