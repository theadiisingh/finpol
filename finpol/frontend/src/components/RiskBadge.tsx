interface RiskBadgeProps {
  score: number
}

function RiskBadge({ score }: RiskBadgeProps) {
  const getColor = (score: number) => {
    if (score >= 80) return 'bg-red-100 text-red-800'
    if (score >= 50) return 'bg-yellow-100 text-yellow-800'
    return 'bg-green-100 text-green-800'
  }

  const getLabel = (score: number) => {
    if (score >= 80) return 'Critical'
    if (score >= 50) return 'Medium'
    return 'Low'
  }

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${getColor(score)}`}>
      {score}% - {getLabel(score)}
    </span>
  )
}

export default RiskBadge
