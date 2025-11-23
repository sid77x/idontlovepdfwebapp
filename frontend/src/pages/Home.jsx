import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { FileText, ArrowRight, Zap, Shield, Cloud } from 'lucide-react'

const Home = () => {
  const features = [
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Process your PDFs in seconds with our optimized engines'
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description: 'Your files are processed locally and never stored on our servers'
    },
    {
      icon: Cloud,
      title: 'No Installation',
      description: 'Work directly in your browser without downloading any software'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="flex justify-center mb-8">
              <div className="flex items-center justify-center w-20 h-20 bg-primary-500 rounded-3xl">
                <FileText className="w-10 h-10 text-white" />
              </div>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              I Don't Love PDF
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto text-balance">
              The free, easy-to-use PDF toolkit that makes working with documents a breeze. 
              No registration, no ads, just powerful PDF tools at your fingertips.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/tools"
                className="btn-primary inline-flex items-center space-x-2 text-lg px-8 py-4"
              >
                <span>Get Started</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              
              <a
                href="#features"
                className="btn-secondary inline-flex items-center space-x-2 text-lg px-8 py-4"
              >
                <span>Learn More</span>
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Why Choose I Don't Love PDF?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              We've built the most comprehensive PDF toolkit with your privacy and efficiency in mind.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  viewport={{ once: true }}
                  className="text-center"
                >
                  <div className="flex justify-center mb-6">
                    <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center">
                      <IconComponent className="w-8 h-8 text-primary-600" />
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    {feature.title}
                  </h3>
                  
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-50 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
              Ready to Transform Your PDFs?
            </h2>
            
            <p className="text-lg text-gray-600 mb-8">
              Join thousands of users who trust I Don't Love PDF for their document needs.
            </p>
            
            <Link
              to="/tools"
              className="btn-primary inline-flex items-center space-x-2 text-lg px-8 py-4"
            >
              <span>Start Processing</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Home