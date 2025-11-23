import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, File, X, AlertCircle } from 'lucide-react'

const FileUpload = ({ 
  onFilesSelected, 
  acceptedTypes = '.pdf', 
  multiple = false, 
  maxSize = 50 * 1024 * 1024, // 50MB
  className = '' 
}) => {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [errors, setErrors] = useState([])

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setErrors([])
    
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const errorMessages = rejectedFiles.map(({ file, errors }) => {
        const errorTypes = errors.map(error => error.code)
        if (errorTypes.includes('file-too-large')) {
          return `${file.name}: File too large (max ${maxSize / 1024 / 1024}MB)`
        }
        if (errorTypes.includes('file-invalid-type')) {
          return `${file.name}: Invalid file type`
        }
        return `${file.name}: Upload error`
      })
      setErrors(errorMessages)
    }

    // Handle accepted files
    if (acceptedFiles.length > 0) {
      const newFiles = multiple 
        ? [...selectedFiles, ...acceptedFiles]
        : acceptedFiles

      setSelectedFiles(newFiles)
      onFilesSelected(newFiles)
    }
  }, [selectedFiles, multiple, maxSize, onFilesSelected])

  const removeFile = (fileToRemove) => {
    const newFiles = selectedFiles.filter(file => file !== fileToRemove)
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    multiple,
    maxSize,
  })

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Zone */}
      <motion.div
        {...getRootProps()}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={`upload-zone cursor-pointer ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center space-y-4">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors duration-200 ${
            isDragActive ? 'bg-primary-100' : 'bg-gray-100'
          }`}>
            <Upload className={`w-8 h-8 ${isDragActive ? 'text-primary-600' : 'text-gray-400'}`} />
          </div>
          
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop files here' : 'Upload files'}
            </p>
            <p className="text-sm text-gray-500">
              Drag & drop files here, or click to browse
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {acceptedTypes} • Max {maxSize / 1024 / 1024}MB
            </p>
          </div>
        </div>
      </motion.div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="space-y-2">
          {errors.map((error, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg"
            >
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </motion.div>
          ))}
        </div>
      )}

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">
            Selected Files ({selectedFiles.length})
          </h4>
          {selectedFiles.map((file, index) => (
            <motion.div
              key={`${file.name}-${index}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <File className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
              </div>
              <button
                onClick={() => removeFile(file)}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors duration-200"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

export default FileUpload