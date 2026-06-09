import { useState } from 'react'
import { Copy, Check, TrendingUp, MessageSquare, Target, Zap } from 'lucide-react'
import ScoreCard from './ScoreCard'

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1.5 rounded-lg transition-colors"
    >
      {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

function ProbabilityGauge({ value }) {
  const color = value >= 70 ? '#22c55e' : value >= 40 ? '#eab308' : '#ef4444'
  const circumference = 2 * Math.PI * 40
  const offset = circumference - (value / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-28">
        <svg className="transform -rotate-90 w-28 h-28">
          <circle cx="56" cy="56" r="40" stroke="#1e293b" strokeWidth="8" fill="none" />
          <circle
            cx="56" cy="56" r="40"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{value}%</span>
          <span className="text-xs text-slate-400">closing</span>
        </div>
      </div>
    </div>
  )
}

export default function ResultsPanel({ result }) {
  if (!result) return null

  const { 
    email_drafts = [], 
    closing_probability = 0, 
    sentiment_score, 
    urgency_score, 
    predicted_response_rate, 
    icp_score, 
    industry, 
    funding_stage, 
    persona, 
    strongest_alignment, 
    visual_key_insight, 
    sources_found, 
    total_time_seconds 
  } = result

  const messageLabels = ['Appreciation', 'Authority', 'Value']
  const messageColors = ['from-blue-600 to-blue-700', 'from-purple-600 to-purple-700', 'from-green-600 to-green-700']

  return (
    <div className="space-y-5 fade-in">
      <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
        <div className="flex items-center gap-2 mb-5">
          <TrendingUp size={18} className="text-blue-400" />
          <h3 className="text-lg font-semibold text-white">Prospect Scores</h3>
          <span className="ml-auto text-xs text-slate-500">{total_time_seconds}s • {sources_found} sources</span>
        </div>

        <div className="flex items-center gap-6 mb-5">
          <ProbabilityGauge value={closing_probability} />
          <div className="flex-1">
            <p className="text-sm text-slate-400 mb-1">Strongest alignment</p>
            <p className="text-sm text-white leading-relaxed">{strongest_alignment || 'Analyzing...'}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <ScoreCard label="Sentiment" value={sentiment_score} color={sentiment_score === 'hot' || sentiment_score === 'warm' ? 'green' : 'yellow'} />
          <ScoreCard label="Urgency" value={urgency_score} color={urgency_score === 'high' || urgency_score === 'critical' ? 'red' : 'yellow'} />
          <ScoreCard label="Response Rate" value={predicted_response_rate} color="blue" />
          <ScoreCard label="ICP Score" value={icp_score} color={icp_score === 'high' ? 'green' : icp_score === 'medium' ? 'yellow' : 'red'} />
          <ScoreCard label="Industry" value={industry} color="purple" />
          <ScoreCard label="Funding" value={funding_stage} color="blue" />
        </div>

        {visual_key_insight && visual_key_insight !== 'No screenshot provided' && (
          <div className="mt-4 p-3 bg-purple-500 bg-opacity-10 border border-purple-500 border-opacity-30 rounded-xl">
            <p className="text-xs text-purple-400 font-medium mb-1">Visual Insight</p>
            <p className="text-sm text-slate-300">{visual_key_insight}</p>
          </div>
        )}
      </div>

      <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
        <div className="flex items-center gap-2 mb-5">
          <MessageSquare size={18} className="text-green-400" />
          <h3 className="text-lg font-semibold text-white">Three Message Sequence</h3>
        </div>

        <div className="space-y-4">
          {email_drafts.map((draft, index) => (
            <div key={index} className="bg-slate-900 rounded-xl p-4 border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-lg bg-gradient-to-r ${messageColors[index]} text-white`}>
                  Message {index + 1} — {messageLabels[index]}
                </span>
                <CopyButton text={`Subject: ${draft.subject}\n\n${draft.body}`} />
              </div>
              <p className="text-xs text-slate-500 mb-2 font-medium">Subject: {draft.subject}</p>
              <p className="text-sm text-slate-300 leading-relaxed">{draft.body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}