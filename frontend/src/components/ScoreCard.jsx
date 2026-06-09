export default function ScoreCard({ label, value, color }) {
    const colorMap = {
      blue: 'bg-blue-500 bg-opacity-10 border-blue-500 border-opacity-30 text-blue-300',
      green: 'bg-green-500 bg-opacity-10 border-green-500 border-opacity-30 text-green-300',
      yellow: 'bg-yellow-500 bg-opacity-10 border-yellow-500 border-opacity-30 text-yellow-300',
      red: 'bg-red-500 bg-opacity-10 border-red-500 border-opacity-30 text-red-300',
      purple: 'bg-purple-500 bg-opacity-10 border-purple-500 border-opacity-30 text-purple-300',
    }
  
    return (
      <div className={`rounded-xl p-3 ${colorMap[color] || colorMap.blue}`}>
        <p className="text-xs text-slate-400 mb-1">{label}</p>
        <p className="text-sm font-semibold capitalize">{value || 'N/A'}</p>
      </div>
    )
  }