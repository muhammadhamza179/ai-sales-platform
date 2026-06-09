import { useState } from 'react'
import { MessageSquare, Send, TrendingUp, TrendingDown } from 'lucide-react'
import { continueConversation } from '../api'

export default function ConversationContinuation({ companyName, initialProbability }) {
  const [reply, setReply] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [currentProbability, setCurrentProbability] = useState(initialProbability)

  const handleSubmit = async () => {
    if (!reply.trim() || loading) return

    setLoading(true)
    try {
      const response = await continueConversation(companyName, reply, history, currentProbability)
      setResult(response)
      setHistory(prev => [
        ...prev,
        { role: 'prospect', message: reply },
        { role: 'us', message: response.response }
      ])
      setCurrentProbability(response.closing_probability_update)
      setReply('')
    } catch (error) {
      console.error('Conversation error:', error)
    } finally {
      setLoading(false)
    }
  }

  const probabilityChange = result ? result.closing_probability_update - initialProbability : 0

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center gap-2 mb-5">
        <MessageSquare size={18} className="text-purple-400" />
        <h3 className="text-lg font-semibold text-white">Continue Conversation</h3>
      </div>

      {history.length > 0 && (
        <div className="space-y-3 mb-5 max-h-64 overflow-y-auto">
          {history.map((msg, i) => (
            <div key={i} className={`p-3 rounded-xl text-sm ${
              msg.role === 'prospect'
                ? 'bg-slate-900 border border-slate-700 text-slate-300'
                : 'bg-blue-500 bg-opacity-10 border border-blue-500 border-opacity-30 text-blue-200'
            }`}>
              <p className="text-xs font-medium mb-1 opacity-60">
                {msg.role === 'prospect' ? 'Prospect' : 'Your message'}
              </p>
              {msg.message}
            </div>
          ))}
        </div>
      )}

      {result && (
        <div className="mb-4 p-3 bg-green-500 bg-opacity-10 border border-green-500 border-opacity-30 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-green-400 font-medium">Objection: {result.objection_type}</span>
            <span className="flex items-center gap-1 text-xs ml-auto">
              {probabilityChange >= 0
                ? <TrendingUp size={12} className="text-green-400" />
                : <TrendingDown size={12} className="text-red-400" />}
              <span className={probabilityChange >= 0 ? 'text-green-400' : 'text-red-400'}>
                {result.closing_probability_update}% probability
              </span>
            </span>
          </div>
          <p className="text-xs text-slate-400">{result.recommended_next_action}</p>
        </div>
      )}

      <div className="flex gap-3">
        <textarea
          value={reply}
          onChange={(e) => setReply(e.target.value)}
          placeholder="Paste the prospect's reply here..."
          rows={3}
          className="flex-1 bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-colors resize-none"
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !reply.trim()}
          className="self-end bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors"
        >
          {loading
            ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            : <Send size={18} />
          }
        </button>
      </div>
    </div>
  )
}