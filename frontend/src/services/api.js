import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large file operations
})

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const pdfService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Get available services
  async getServices() {
    const response = await api.get('/services')
    return response.data
  },

  // Merge PDFs
  async mergePDFs(files, options = {}) {
    const formData = new FormData()
    files.forEach((file, index) => {
      formData.append('files', file)
    })
    
    if (options.output_filename) {
      formData.append('output_filename', options.output_filename)
    }

    const response = await api.post('/merge', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // Rotate PDF
  async rotatePDF(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options.rotation !== undefined) {
      formData.append('rotation', options.rotation.toString())
    }
    if (options.pages) {
      formData.append('pages', options.pages)
    }

    const response = await api.post('/rotate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // Split PDF
  async splitPDF(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options.pages) {
      formData.append('pages', options.pages)
    }
    if (options.split_type) {
      formData.append('split_type', options.split_type)
    }

    const response = await api.post('/split', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // Protect PDF
  async protectPDF(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options.user_password) {
      formData.append('user_password', options.user_password)
    }
    if (options.owner_password) {
      formData.append('owner_password', options.owner_password)
    }

    const response = await api.post('/protect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // Compress PDF
  async compressPDF(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options.quality) {
      formData.append('quality', options.quality)
    }

    const response = await api.post('/compress', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // Add watermark
  async watermarkPDF(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    // Backend expects 'text' not 'watermark_text'
    if (options.watermark_text) {
      formData.append('text', options.watermark_text)
    }
    if (options.opacity !== undefined) {
      formData.append('opacity', options.opacity.toString())
    }
    if (options.font_size !== undefined) {
      formData.append('font_size', options.font_size.toString())
    }
    if (options.position) {
      formData.append('position', options.position)
    }

    const response = await api.post('/watermark', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // OCR PDF
  async ocrPDF(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options.language) {
      formData.append('language', options.language)
    }

    const response = await api.post('/ocr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  // PDF to Images
  async pdfToImages(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options.format) {
      formData.append('format', options.format)
    }
    if (options.dpi) {
      formData.append('dpi', options.dpi.toString())
    }
    if (options.pages) {
      formData.append('pages', options.pages)
    }

    const response = await api.post('/pdf-to-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // Images to PDF
  async imagesToPDF(files, options = {}) {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    
    if (options.output_filename) {
      formData.append('output_filename', options.output_filename)
    }

    const response = await api.post('/image-to-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  },

  // HTML to PDF
  async htmlToPDF(htmlContent, options = {}) {
    const formData = new FormData()
    
    if (typeof htmlContent === 'string') {
      formData.append('html_content', htmlContent)
    } else {
      formData.append('html_file', htmlContent)
    }
    
    if (options.output_filename) {
      formData.append('output_filename', options.output_filename)
    }

    const response = await api.post('/html-to-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    return response.data
  }
}

export default api