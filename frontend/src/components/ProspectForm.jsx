import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Search, Upload, X, Building2 } from 'lucide-react'

export default function ProspectForm({ onSubmit, loading }) {
  const [companyName, setCompanyName] = useState('')
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [screenshot, setScreenshot] = useState(null)
  const [preview, setPreview] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file) {
      setScreenshot(file)
      setPreview(URL.createObjectURL(file))
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024
  })

  const removeScreenshot = () => {
    setScreenshot(null)
    setPreview(null)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!companyName.trim()) return
    onSubmit(companyName, linkedinUrl, screenshot)
  }

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
          <Building2 size={20} className="text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-white">Prospect Analysis</h2>
          <p className="text-sm text-slate-400">Enter company details to analyze</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Company Name *
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g. Notion, Stripe, Figma"
            className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            LinkedIn URL
          </label>
          <input
            type="url"
            value={linkedinUrl}
            onChange={(e) => setLinkedinUrl(e.target.value)}
            placeholder="https://linkedin.com/company/notion"
            className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Product Screenshot (Optional)
          </label>
          {preview ? (
            <div className="relative rounded-xl overflow-hidden border border-slate-600">
              <img src={preview} alt="Screenshot preview" className="w-full h-40 object-cover" />
              <button
                type="button"
                onClick={removeScreenshot}
                className="absolute top-2 right-2 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
              >
                <X size={16} className="text-white" />
              </button>
              <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 rounded-lg px-2 py-1">
                <p className="text-xs text-white">{screenshot?.name}</p>
              </div>
            </div>
          ) : (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-blue-500 bg-blue-500 bg-opacity-10'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              <input {...getInputProps()} />
              <Upload size={24} className="text-slate-500 mx-auto mb-2" />
              <p className="text-sm text-slate-400">
                {isDragActive ? 'Drop it here' : 'Drag and drop or click to upload'}
              </p>
              <p className="text-xs text-slate-600 mt-1">PNG, JPG up to 5MB</p>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading || !companyName.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Search size={18} />
              Analyze Prospect
            </>
          )}
        </button>
      </form>
    </div>
  )
}