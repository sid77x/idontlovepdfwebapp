import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ToolGrid from '../components/ToolGrid'
import FileUpload from '../components/FileUpload'
import ProcessingQueue from '../components/ProcessingQueue'
import ToolModal from '../components/ToolModal'

const Tools = () => {
  const [selectedTool, setSelectedTool] = useState(null)
  const [showModal, setShowModal] = useState(false)

  const handleToolSelect = (tool) => {
    setSelectedTool(tool)
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setSelectedTool(null)
  }

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            PDF Tools
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Select a tool below to get started with your PDF processing needs. 
            All tools are free and work directly in your browser.
          </p>
        </motion.div>

        {/* Tool Grid */}
        <ToolGrid onToolSelect={handleToolSelect} />

        {/* Tool Modal */}
        <AnimatePresence>
          {showModal && selectedTool && (
            <ToolModal 
              tool={selectedTool} 
              onClose={closeModal}
            />
          )}
        </AnimatePresence>

        {/* Processing Queue */}
        <ProcessingQueue />
      </div>
    </div>
  )
}

export default Tools