import { createContext, useContext, useReducer } from 'react'

const ProcessingContext = createContext()

const initialState = {
  jobs: [],
  activeJobs: 0,
  completedJobs: 0,
  failedJobs: 0
}

const processingReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_JOB':
      return {
        ...state,
        jobs: [...state.jobs, action.payload],
        activeJobs: state.activeJobs + 1
      }
    case 'UPDATE_JOB_PROGRESS':
      return {
        ...state,
        jobs: state.jobs.map(job =>
          job.id === action.payload.id
            ? { ...job, progress: action.payload.progress }
            : job
        )
      }
    case 'COMPLETE_JOB':
      return {
        ...state,
        jobs: state.jobs.map(job =>
          job.id === action.payload.id
            ? { ...job, status: 'completed', downloadUrl: action.payload.downloadUrl, progress: 100 }
            : job
        ),
        activeJobs: state.activeJobs - 1,
        completedJobs: state.completedJobs + 1
      }
    case 'FAIL_JOB':
      return {
        ...state,
        jobs: state.jobs.map(job =>
          job.id === action.payload.id
            ? { ...job, status: 'failed', error: action.payload.error }
            : job
        ),
        activeJobs: state.activeJobs - 1,
        failedJobs: state.failedJobs + 1
      }
    case 'REMOVE_JOB':
      const job = state.jobs.find(j => j.id === action.payload)
      return {
        ...state,
        jobs: state.jobs.filter(j => j.id !== action.payload),
        ...(job?.status === 'completed' && { completedJobs: state.completedJobs - 1 }),
        ...(job?.status === 'failed' && { failedJobs: state.failedJobs - 1 })
      }
    case 'CLEAR_JOBS':
      return initialState
    default:
      return state
  }
}

export const ProcessingProvider = ({ children }) => {
  const [state, dispatch] = useReducer(processingReducer, initialState)

  return (
    <ProcessingContext.Provider value={{ state, dispatch }}>
      {children}
    </ProcessingContext.Provider>
  )
}

export const useProcessing = () => {
  const context = useContext(ProcessingContext)
  if (!context) {
    throw new Error('useProcessing must be used within a ProcessingProvider')
  }
  return context
}