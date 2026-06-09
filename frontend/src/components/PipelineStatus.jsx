import { CheckCircle, Circle, Loader, AlertCircle } from 'lucide-react'

const PIPELINE_STEPS = [
  { key: 'research', label: 'Web Research', desc: 'Searching company news, funding, tech stack' },
  { key: 'linkedin', label: 'LinkedIn Analysis', desc: 'Analyzing company profile and signals' },
  { key: 'vision', label: 'Screenshot Analysis', desc: 'Reading product UI with computer vision' },
  { key: 'persona_scoring', label: 'Scoring Prospect', desc: 'Calculating closing probability and sentiment' },
  { key: 'alignment', label: 'Company Alignment', desc: 'Finding strongest match with your expertise' },
  { key: 'outreach', label: 'Writing Messages', desc: 'Generating three message sequence' },
  { key: 'crm', label: 'HubSpot CRM', desc: 'Creating contact and saving analysis' },
]

export default function PipelineStatus({ status, currentStep, completedSteps, errors }) {
  if (status === 'idle') return null

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700 fade-in">
      <h3 className="text-lg font-semibold text-white mb-5">
        {status === 'running' ? 'Agent Running...' : status === 'complete' ? 'Analysis Complete' : 'Analysis Failed'}
      </h3>

      <div className="space-y-3">
        {PIPELINE_STEPS.map((step) => {
          const isCompleted = completedSteps.includes(step.key)
          const isCurrent = currentStep === step.key
          const hasError = errors.some(e => e.includes(step.key))

          return (
            <div key={step.key} className={`flex items-start gap-3 p-3 rounded-xl transition-all ${
              isCurrent ? 'bg-blue-500 bg-opacity-10 border border-blue-500 border-opacity-30' :
              isCompleted ? 'opacity-70' : 'opacity-40'
            }`}>
              <div className="mt-0.5 flex-shrink-0">
                {isCompleted ? (
                  <CheckCircle size={20} className="text-green-400" />
                ) : isCurrent ? (
                  <Loader size={20} className="text-blue-400 animate-spin" />
                ) : hasError ? (
                  <AlertCircle size={20} className="text-red-400" />
                ) : (
                  <Circle size={20} className="text-slate-600" />
                )}
              </div>
              <div>
                <p className={`text-sm font-medium ${
                  isCurrent ? 'text-blue-300' :
                  isCompleted ? 'text-green-300' :
                  hasError ? 'text-red-300' :
                  'text-slate-500'
                }`}>
                  {step.label}
                </p>
                {isCurrent && (
                  <p className="text-xs text-slate-400 mt-0.5">{step.desc}</p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {errors.length > 0 && (
        <div className="mt-4 p-3 bg-red-500 bg-opacity-10 border border-red-500 border-opacity-30 rounded-xl">
          <p className="text-xs text-red-400 font-medium mb-1">Errors (non-critical):</p>
          {errors.map((error, i) => (
            <p key={i} className="text-xs text-red-300">{error.slice(0, 80)}...</p>
          ))}
        </div>
      )}
    </div>
  )
}