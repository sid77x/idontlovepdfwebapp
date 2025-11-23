import { motion } from 'framer-motion'
import { 
  FileText, 
  Merge, 
  RotateCw, 
  Split, 
  Shield, 
  Minimize2, 
  Droplets,
  Search,
  Image,
  ImagePlus,
  Code,
  Hash,
  Crop,
  Wrench,
  FileText as FileWord,
  FileSpreadsheet,
  Presentation,
  Globe
} from 'lucide-react'

const tools = [
  {
    id: 'merge',
    name: 'Merge PDFs',
    description: 'Combine multiple PDF files into one document',
    icon: Merge,
    color: 'bg-blue-500',
    available: true
  },
  {
    id: 'rotate',
    name: 'Rotate PDF',
    description: 'Rotate pages in your PDF document',
    icon: RotateCw,
    color: 'bg-green-500',
    available: true
  },
  {
    id: 'split',
    name: 'Split PDF',
    description: 'Extract pages or split PDF into multiple files',
    icon: Split,
    color: 'bg-purple-500',
    available: true
  },
  {
    id: 'protect',
    name: 'Protect PDF',
    description: 'Add password protection to your PDF',
    icon: Shield,
    color: 'bg-red-500',
    available: true
  },
  {
    id: 'compress',
    name: 'Compress PDF',
    description: 'Reduce PDF file size while maintaining quality',
    icon: Minimize2,
    color: 'bg-orange-500',
    available: true
  },
  {
    id: 'watermark',
    name: 'Watermark PDF',
    description: 'Add text or image watermarks to your PDF',
    icon: Droplets,
    color: 'bg-teal-500',
    available: true
  },
  {
    id: 'ocr',
    name: 'OCR PDF',
    description: 'Extract text from scanned documents',
    icon: Search,
    color: 'bg-indigo-500',
    available: true
  },
  {
    id: 'pdf-to-image',
    name: 'PDF to Images',
    description: 'Convert PDF pages to image files',
    icon: Image,
    color: 'bg-pink-500',
    available: true
  },
  {
    id: 'image-to-pdf',
    name: 'Images to PDF',
    description: 'Convert image files to PDF document',
    icon: ImagePlus,
    color: 'bg-yellow-500',
    available: true
  },
  {
    id: 'html-to-pdf',
    name: 'HTML to PDF',
    description: 'Convert HTML content to PDF document',
    icon: Code,
    color: 'bg-cyan-500',
    available: true
  },
  {
    id: 'page-numbers',
    name: 'Page Numbers',
    description: 'Add page numbers to your PDF',
    icon: Hash,
    color: 'bg-violet-500',
    available: false
  },
  {
    id: 'crop',
    name: 'Crop PDF',
    description: 'Crop PDF pages to specific dimensions',
    icon: Crop,
    color: 'bg-lime-500',
    available: false
  },
  {
    id: 'repair',
    name: 'Repair PDF',
    description: 'Fix corrupted or damaged PDF files',
    icon: Wrench,
    color: 'bg-amber-500',
    available: false
  },
  {
    id: 'pdf-to-word',
    name: 'PDF to Word',
    description: 'Convert PDF to editable Word document',
    icon: FileWord,
    color: 'bg-blue-600',
    available: false
  },
  {
    id: 'word-to-pdf',
    name: 'Word to PDF',
    description: 'Convert Word documents to PDF',
    icon: FileWord,
    color: 'bg-blue-700',
    available: false
  },
  {
    id: 'pdf-to-excel',
    name: 'PDF to Excel',
    description: 'Convert PDF tables to Excel spreadsheet',
    icon: FileSpreadsheet,
    color: 'bg-green-600',
    available: false
  },
  {
    id: 'excel-to-pdf',
    name: 'Excel to PDF',
    description: 'Convert Excel spreadsheets to PDF',
    icon: FileSpreadsheet,
    color: 'bg-green-700',
    available: false
  },
  {
    id: 'pdf-to-html',
    name: 'PDF to HTML',
    description: 'Convert PDF to HTML web page',
    icon: Globe,
    color: 'bg-sky-500',
    available: false
  },
  {
    id: 'pdf-to-powerpoint',
    name: 'PDF to PowerPoint',
    description: 'Convert PDF to PowerPoint presentation',
    icon: Presentation,
    color: 'bg-orange-600',
    available: false
  },
  {
    id: 'powerpoint-to-pdf',
    name: 'PowerPoint to PDF',
    description: 'Convert PowerPoint to PDF',
    icon: Presentation,
    color: 'bg-orange-700',
    available: false
  }
]

const ToolGrid = ({ onToolSelect }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {tools.map((tool, index) => {
        const IconComponent = tool.icon
        
        return (
          <motion.div
            key={tool.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ y: -5 }}
            className={`card cursor-pointer transition-all duration-200 hover:shadow-lg ${
              !tool.available ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={() => tool.available && onToolSelect(tool)}
          >
            <div className="flex flex-col items-center text-center space-y-4">
              <div className={`w-16 h-16 ${tool.color} rounded-2xl flex items-center justify-center`}>
                <IconComponent className="w-8 h-8 text-white" />
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {tool.name}
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {tool.description}
                </p>
              </div>
              
              {!tool.available && (
                <div className="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded-full">
                  Coming Soon
                </div>
              )}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

export default ToolGrid