import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Tools from './pages/Tools'
import About from './pages/About'
import { ProcessingProvider } from './contexts/ProcessingContext'

function App() {
  return (
    <ProcessingProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
          <Navbar />
          <motion.main
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="pt-16"
          >
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/tools" element={<Tools />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </motion.main>
        </div>
      </Router>
    </ProcessingProvider>
  )
}

export default App