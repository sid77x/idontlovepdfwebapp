import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { X, Settings, Play, Download, AlertCircle } from 'lucide-react'
import FileUpload from './FileUpload'
import { useProcessing } from '../contexts/ProcessingContext'
import { pdfService } from '../services/api'

const ToolModal = ({ tool, onClose }) => {
  const [files, setFiles] = useState([])
  const [options, setOptions] = useState({})
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [processedFile, setProcessedFile] = useState(null)
  const [fileStats, setFileStats] = useState({ inputSize: 0, outputSize: 0 })
  const { dispatch } = useProcessing()

  // Reset state when tool changes
  useEffect(() => {
    setFiles([])
    setOptions({})
    setError(null)
    setSuccess(false)
    setProcessedFile(null)
    setFileStats({ inputSize: 0, outputSize: 0 })
  }, [tool])

  const getAcceptedFileTypes = () => {
    switch (tool.id) {
      case 'image-to-pdf':
        return '.jpg,.jpeg,.png,.gif,.bmp,.tiff'
      case 'html-to-pdf':
        return '.html,.htm'
      default:
        return '.pdf'
    }
  }

  const getMultipleFiles = () => {
    return ['merge', 'image-to-pdf'].includes(tool.id)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const getOperationResult = () => {
    const { inputSize, outputSize } = fileStats
    const diff = inputSize - outputSize
    const percentChange = inputSize > 0 ? ((diff / inputSize) * 100).toFixed(1) : 0

    switch (tool.id) {
      case 'compress':
        if (diff > 0) {
          return `Reduced by ${formatFileSize(diff)} (${percentChange}% smaller)`
        }
        return 'File compressed successfully'
      
      case 'rotate':
        const pages = options.pages || 'all'
        const angle = options.rotation || 90
        return `Rotated ${pages === 'all' ? 'all pages' : pages} by ${angle}°`
      
      case 'protect':
        return 'Password protection added successfully'
      
      case 'merge':
        return `Merged ${files.length} PDFs into 1 document`
      
      case 'split':
        return 'PDF split successfully'
      
      case 'watermark':
        return 'Watermark added successfully'
      
      case 'ocr':
        return 'Text extracted successfully'
      
      case 'pdf-to-image':
        return 'PDF converted to images'
      
      case 'image-to-pdf':
        return `Converted ${files.length} image(s) to PDF`
      
      case 'html-to-pdf':
        return 'HTML converted to PDF successfully'
      
      default:
        return 'Processing complete'
    }
  }

  const handleDownload = () => {
    if (processedFile) {
      const link = document.createElement('a')
      link.href = processedFile.url
      link.download = processedFile.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleProcessAnother = () => {
    setFiles([])
    setOptions({})
    setError(null)
    setSuccess(false)
    setProcessedFile(null)
    setFileStats({ inputSize: 0, outputSize: 0 })
  }

  const renderToolOptions = () => {
    switch (tool.id) {
      case 'rotate':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rotation Angle
              </label>
              <select
                value={options.rotation || 90}
                onChange={(e) => setOptions({ ...options, rotation: parseInt(e.target.value) })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value={90}>90° Clockwise</option>
                <option value={180}>180°</option>
                <option value={270}>270° Clockwise</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pages (optional)
              </label>
              <input
                type="text"
                value={options.pages || ''}
                onChange={(e) => setOptions({ ...options, pages: e.target.value })}
                placeholder="e.g., 1,2,5-10 or leave empty for all pages"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        )
      
      case 'split':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Split Type
              </label>
              <select
                value={options.split_type || 'pages'}
                onChange={(e) => setOptions({ ...options, split_type: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="pages">Extract specific pages</option>
                <option value="range">Split by page ranges</option>
                <option value="each">Split each page separately</option>
              </select>
            </div>
            {options.split_type !== 'each' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pages/Ranges
                </label>
                <input
                  type="text"
                  value={options.pages || ''}
                  onChange={(e) => setOptions({ ...options, pages: e.target.value })}
                  placeholder="e.g., 1,2,5-10"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            )}
          </div>
        )
      
      case 'protect':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                User Password
              </label>
              <input
                type="password"
                value={options.user_password || ''}
                onChange={(e) => setOptions({ ...options, user_password: e.target.value })}
                placeholder="Password to open the PDF"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Owner Password (optional)
              </label>
              <input
                type="password"
                value={options.owner_password || ''}
                onChange={(e) => setOptions({ ...options, owner_password: e.target.value })}
                placeholder="Password for editing permissions"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        )
      
      case 'compress':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compression Quality
            </label>
            <select
              value={options.quality || 'medium'}
              onChange={(e) => setOptions({ ...options, quality: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="low">Low Quality (Highest Compression)</option>
              <option value="medium">Medium Quality</option>
              <option value="high">High Quality (Low Compression)</option>
            </select>
          </div>
        )
      
      case 'watermark':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Watermark Text
              </label>
              <input
                type="text"
                value={options.watermark_text || ''}
                onChange={(e) => setOptions({ ...options, watermark_text: e.target.value })}
                placeholder="Enter watermark text"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Opacity ({options.opacity || 50}%)
              </label>
              <input
                type="range"
                min="10"
                max="100"
                value={options.opacity || 50}
                onChange={(e) => setOptions({ ...options, opacity: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>
          </div>
        )
      
      case 'ocr':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              value={options.language || 'eng'}
              onChange={(e) => setOptions({ ...options, language: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="eng">English</option>
              <option value="spa">Spanish</option>
              <option value="fra">French</option>
              <option value="deu">German</option>
              <option value="ita">Italian</option>
            </select>
          </div>
        )
      
      case 'pdf-to-image':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Image Format
              </label>
              <select
                value={options.format || 'png'}
                onChange={(e) => setOptions({ ...options, format: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="png">PNG</option>
                <option value="jpg">JPG</option>
                <option value="tiff">TIFF</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                DPI Quality
              </label>
              <select
                value={options.dpi || 150}
                onChange={(e) => setOptions({ ...options, dpi: parseInt(e.target.value) })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value={72}>72 DPI (Low)</option>
                <option value={150}>150 DPI (Medium)</option>
                <option value={300}>300 DPI (High)</option>
              </select>
            </div>
          </div>
        )
      
      case 'html-to-pdf':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Output Filename (optional)
            </label>
            <input
              type="text"
              value={options.output_filename || ''}
              onChange={(e) => setOptions({ ...options, output_filename: e.target.value })}
              placeholder="converted-document.pdf"
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        )
      
      default:
        return null
    }
  }

  const processFiles = async () => {
    if (files.length === 0) {
      setError('Please select at least one file')
      return
    }

    setIsProcessing(true)
    setError(null)

    const jobId = Date.now()
    const job = {
      id: jobId,
      filename: files.length > 1 ? `${files.length} files` : files[0].name,
      operation: tool.name.toLowerCase(),
      status: 'processing',
      progress: 0
    }

    dispatch({ type: 'ADD_JOB', payload: job })

    try {
      // Calculate input file size(s)
      const inputSize = files.reduce((sum, file) => sum + file.size, 0)

      let result
      
      switch (tool.id) {
        case 'merge':
          result = await pdfService.mergePDFs(files, options)
          break
        case 'rotate':
          result = await pdfService.rotatePDF(files[0], options)
          break
        case 'split':
          result = await pdfService.splitPDF(files[0], options)
          break
        case 'protect':
          result = await pdfService.protectPDF(files[0], options)
          break
        case 'compress':
          result = await pdfService.compressPDF(files[0], options)
          break
        case 'watermark':
          result = await pdfService.watermarkPDF(files[0], options)
          break
        case 'ocr':
          result = await pdfService.ocrPDF(files[0], options)
          break
        case 'pdf-to-image':
          result = await pdfService.pdfToImages(files[0], options)
          break
        case 'image-to-pdf':
          result = await pdfService.imagesToPDF(files, options)
          break
        case 'html-to-pdf':
          result = await pdfService.htmlToPDF(files[0], options)
          break
        default:
          throw new Error('Unsupported operation')
      }

      // Create download URL
      const blob = new Blob([result], { type: 'application/pdf' })
      const downloadUrl = URL.createObjectURL(blob)
      const outputSize = blob.size
      const outputFilename = options.output_filename || `processed_${files[0]?.name || 'document'}`

      // Update file stats
      setFileStats({ inputSize, outputSize })

      // Set processed file info
      setProcessedFile({
        url: downloadUrl,
        filename: outputFilename
      })

      dispatch({ 
        type: 'COMPLETE_JOB', 
        payload: { 
          id: jobId, 
          downloadUrl,
          outputFilename
        }
      })

      // Show success state instead of closing
      setSuccess(true)

    } catch (error) {
      console.error('Processing error:', error)
      dispatch({ 
        type: 'FAIL_JOB', 
        payload: { 
          id: jobId, 
          error: error.response?.data?.detail || error.message || 'Processing failed'
        }
      })
      setError(error.response?.data?.detail || error.message || 'Processing failed')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 ${tool.color} rounded-xl flex items-center justify-center`}>
              <tool.icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{tool.name}</h2>
              <p className="text-sm text-gray-500">{tool.description}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {success ? (
            /* Success State */
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-6"
            >
              {/* Success Icon */}
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Processing Complete!</h3>
                  <p className="text-sm text-gray-600">{getOperationResult()}</p>
                </div>
              </div>

              {/* File Size Information */}
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600">Original Size:</span>
                  <span className="font-medium text-gray-900">{formatFileSize(fileStats.inputSize)}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600">Final Size:</span>
                  <span className="font-medium text-gray-900">{formatFileSize(fileStats.outputSize)}</span>
                </div>
                {tool.id === 'compress' && fileStats.inputSize > fileStats.outputSize && (
                  <div className="flex justify-between items-center text-sm pt-2 border-t border-gray-200">
                    <span className="text-gray-600">Size Difference:</span>
                    <span className="font-medium text-green-600">
                      -{formatFileSize(fileStats.inputSize - fileStats.outputSize)}
                    </span>
                  </div>
                )}
              </div>

              {/* Download Button */}
              <button
                onClick={handleDownload}
                className="w-full btn-primary flex items-center justify-center space-x-2 py-3"
              >
                <Download className="w-5 h-5" />
                <span>Download Processed File</span>
              </button>
            </motion.div>
          ) : (
            /* Upload & Options State */
            <div className="space-y-6">
              {/* File Upload */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center space-x-2">
                  <span>Select Files</span>
                </h3>
                <FileUpload
                  onFilesSelected={setFiles}
                  acceptedTypes={getAcceptedFileTypes()}
                  multiple={getMultipleFiles()}
                />
              </div>

              {/* Tool Options */}
              {renderToolOptions() && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center space-x-2">
                    <Settings className="w-5 h-5" />
                    <span>Options</span>
                  </h3>
                  {renderToolOptions()}
                </div>
              )}

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center space-x-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg"
                >
                  <AlertCircle className="w-4 h-4" />
                  <span>{error}</span>
                </motion.div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          {success ? (
            /* Success Footer */
            <div className="flex items-center justify-end space-x-3">
              <button
                onClick={handleProcessAnother}
                className="btn-secondary"
              >
                Process Another File
              </button>
              <button
                onClick={onClose}
                className="btn-primary"
              >
                Close
              </button>
            </div>
          ) : (
            /* Processing Footer */
            <div className="flex items-center justify-end space-x-3">
              <button
                onClick={onClose}
                disabled={isProcessing}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={processFiles}
                disabled={isProcessing || files.length === 0}
                className="btn-primary flex items-center space-x-2"
              >
                {isProcessing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Process Files</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default ToolModal