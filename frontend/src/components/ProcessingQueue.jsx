import { motion } from 'framer-motion'
import { CheckCircle, XCircle, Download, Trash2, RefreshCw } from 'lucide-react'
import { useProcessing } from '../contexts/ProcessingContext'

const ProgressBar = ({ progress }) => (
  <div className="w-full bg-gray-200 rounded-full h-2">
    <motion.div
      className="bg-primary-500 h-2 rounded-full"
      initial={{ width: 0 }}
      animate={{ width: `${progress}%` }}
      transition={{ duration: 0.3 }}
    />
  </div>
)

const ProcessingQueue = () => {
  const { state, dispatch } = useProcessing()

  if (state.jobs.length === 0) {
    return null
  }

  const downloadFile = (job) => {
    if (job.downloadUrl) {
      const link = document.createElement('a')
      link.href = job.downloadUrl
      link.download = job.outputFilename || `processed_${job.filename}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const removeJob = (jobId) => {
    dispatch({ type: 'REMOVE_JOB', payload: jobId })
  }

  const clearAllJobs = () => {
    dispatch({ type: 'CLEAR_JOBS' })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 right-6 w-96 max-h-96 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden z-50"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">
            Processing Queue ({state.jobs.length})
          </h3>
          <button
            onClick={clearAllJobs}
            className="text-xs text-gray-500 hover:text-red-500 transition-colors duration-200"
          >
            Clear All
          </button>
        </div>
        
        {/* Stats */}
        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-600">
          {state.activeJobs > 0 && (
            <span className="flex items-center space-x-1">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>{state.activeJobs} active</span>
            </span>
          )}
          {state.completedJobs > 0 && (
            <span className="flex items-center space-x-1">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span>{state.completedJobs} completed</span>
            </span>
          )}
          {state.failedJobs > 0 && (
            <span className="flex items-center space-x-1">
              <XCircle className="w-3 h-3 text-red-500" />
              <span>{state.failedJobs} failed</span>
            </span>
          )}
        </div>
      </div>

      {/* Job List */}
      <div className="max-h-64 overflow-y-auto">
        {state.jobs.map((job) => (
          <motion.div
            key={job.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="p-4 border-b border-gray-100 last:border-b-0"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {job.filename}
                </p>
                <p className="text-xs text-gray-500 capitalize">
                  {job.operation} • {job.status}
                </p>
                
                {/* Progress Bar */}
                {job.status === 'processing' && (
                  <div className="mt-2">
                    <ProgressBar progress={job.progress || 0} />
                  </div>
                )}
                
                {/* Error Message */}
                {job.status === 'failed' && job.error && (
                  <p className="text-xs text-red-600 mt-1">{job.error}</p>
                )}
              </div>
              
              {/* Actions */}
              <div className="flex items-center space-x-2 ml-3">
                {job.status === 'completed' && (
                  <button
                    onClick={() => downloadFile(job)}
                    className="p-1 text-green-600 hover:text-green-700 transition-colors duration-200"
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                )}
                
                {job.status === 'processing' && (
                  <div className="w-4 h-4">
                    <RefreshCw className="w-4 h-4 text-primary-500 animate-spin" />
                  </div>
                )}
                
                {job.status === 'failed' && (
                  <div className="w-4 h-4">
                    <XCircle className="w-4 h-4 text-red-500" />
                  </div>
                )}
                
                <button
                  onClick={() => removeJob(job.id)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors duration-200"
                  title="Remove"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

export default ProcessingQueue