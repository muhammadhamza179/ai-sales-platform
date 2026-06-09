import { useState } from 'react'
import { Brain, Zap } from 'lucide-react'
import ProspectForm from './components/ProspectForm'
import PipelineStatus from './components/PipelineStatus'
import ResultsPanel from './components/ResultsPanel'
import ConversationContinuation from './components/ConversationContinuation'
import { analyzeProspect } from './api'

const PIPELINE_ORDER = ['research', 'linkedin', 'vision', 'persona_scoring', 'alignment', 'outreach', 'crm']

export default function App() {
  const [status, setStatus] = useState('idle')
  const [currentStep, setCurrentStep] = useState(null)
  const [completedSteps, setCompletedSteps] = useState([])
  const [result, setResult] = useState(null)
  const [errors, setErrors] = useState([])
  const [loading, setLoading] = useState(false)

  const simulatePipelineProgress = (totalSeconds) => {
    const timePerStep = (totalSeconds * 1000) / PIPELINE_ORDER.length
    PIPELINE_ORDER.forEach((step, index) => {
      setTimeout(() => {
        setCurrentStep(step)
        if (index > 0) {
          setCompletedSteps(prev => [...prev, PIPELINE_ORDER[index - 1]])
        }
      }, timePerStep * index)
    })
  }

  const handleAnalyze = async (companyName, linkedinUrl, screenshot) => {
    setLoading(true)
    setStatus('running')
    setCompletedSteps([])
    setCurrentStep('research')
    setResult(null)
    setErrors([])

    simulatePipelineProgress(35)

    try {
      const data = await analyzeProspect(companyName, linkedinUrl, screenshot)
      setCompletedSteps(PIPELINE_ORDER)
      setCurrentStep(null)
      setResult(data)
      setErrors(data.errors || [])
      setStatus('complete')
    } catch (error) {
      setStatus('error')
      setErrors([error.message || 'Pipeline failed'])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="border-b border-slate-800 bg-slate-900 bg-opacity-80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Brain size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-base font-bold text-white">AI Sales Platform</h1>
              <p className="text-xs text-slate-500">Agentic B2B Intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 text-xs text-green-400">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Live
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 bg-blue-500 bg-opacity-10 border border-blue-500 border-opacity-20 rounded-full px-4 py-1.5 text-xs text-blue-400 mb-4">
            <Zap size={12} />
            Multimodal AI Agent — Web Research + Computer Vision + Predictive Scoring
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">
            Research any prospect in 30 seconds
          </h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            Drop a company name and screenshot. The agent researches the web, analyzes the product UI, scores closing probability, and writes three personalized messages automatically.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-5">
            <ProspectForm onSubmit={handleAnalyze} loading={loading} />
            <PipelineStatus
              status={status}
              currentStep={currentStep}
              completedSteps={completedSteps}
              errors={errors}
            />
          </div>

          <div className="lg:col-span-2 space-y-5">
            {result ? (
              <>
                <ResultsPanel result={result} />
                <ConversationContinuation
                  companyName={result.company_name}
                  initialProbability={result.closing_probability}
                />
              </>
            ) : (
              <div className="h-full min-h-64 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-slate-700">
                    <Brain size={28} className="text-slate-600" />
                  </div>
                  <p className="text-slate-500 text-sm">Enter a company name to start the analysis</p>
                  <p className="text-slate-600 text-xs mt-1">Results appear here in real time</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}