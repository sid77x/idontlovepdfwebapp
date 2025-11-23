import { motion } from 'framer-motion'
import { Github, Mail, Heart, Code, Zap, Users } from 'lucide-react'

const About = () => {
  const stats = [
    { label: 'PDF Tools Available', value: '10+' },
    { label: 'Files Processed', value: '∞' },
    { label: 'User Privacy', value: '100%' },
    { label: 'Cost to Use', value: '$0' }
  ]

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            About I Don't Love PDF
          </h1>
          <p className="text-lg text-gray-600">
            The story behind the free PDF toolkit that prioritizes your privacy
          </p>
        </motion.div>

        {/* Mission */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="card mb-12"
        >
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                <Heart className="w-6 h-6 text-primary-600" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Mission</h2>
              <p className="text-gray-600 leading-relaxed mb-4">
                We believe that working with PDFs shouldn't be complicated, expensive, or compromise your privacy. 
                That's why we created I Don't Love PDF - a completely free, open-source toolkit that processes 
                your documents locally in your browser.
              </p>
              <p className="text-gray-600 leading-relaxed">
                No registration required, no file uploads to unknown servers, no hidden costs. 
                Just powerful PDF tools that respect your privacy and get the job done.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Stats */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12"
        >
          {stats.map((stat, index) => (
            <div key={index} className="card text-center">
              <div className="text-2xl font-bold text-primary-600 mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600">
                {stat.label}
              </div>
            </div>
          ))}
        </motion.section>

        {/* Features */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="card mb-12"
        >
          <div className="flex items-start space-x-4 mb-6">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">What Makes Us Different</h2>
            </div>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Privacy First</h3>
              <p className="text-gray-600 mb-4">
                All processing happens in your browser. Your files never leave your device, 
                ensuring complete privacy and security.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Always Free</h3>
              <p className="text-gray-600 mb-4">
                No premium plans, no usage limits, no hidden fees. 
                All features are completely free forever.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Open Source</h3>
              <p className="text-gray-600 mb-4">
                Our code is open for everyone to see, audit, and contribute to. 
                Transparency builds trust.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Registration</h3>
              <p className="text-gray-600 mb-4">
                Start using our tools immediately. No accounts, no passwords, 
                no personal information required.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Technology */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
          className="card mb-12"
        >
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <Code className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Built with Modern Technology</h2>
              <p className="text-gray-600 leading-relaxed mb-4">
                I Don't Love PDF is built using cutting-edge web technologies including React, 
                FastAPI microservices, and WebAssembly for high-performance PDF processing 
                directly in your browser.
              </p>
              <p className="text-gray-600 leading-relaxed">
                Our microservices architecture ensures reliability, scalability, and easy maintenance 
                while keeping everything fast and responsive.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Contact */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          viewport={{ once: true }}
          className="card"
        >
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Get Involved</h2>
              <p className="text-gray-600 leading-relaxed mb-6">
                I Don't Love PDF is a community project. Whether you want to report a bug, 
                suggest a feature, or contribute code, we'd love to hear from you.
              </p>
              
              <div className="flex flex-wrap gap-4">
                <a
                  href="https://github.com/yourusername/idontlovepdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 btn-secondary"
                >
                  <Github className="w-4 h-4" />
                  <span>View on GitHub</span>
                </a>
                
                <a
                  href="mailto:hello@idontlovepdf.com"
                  className="inline-flex items-center space-x-2 btn-secondary"
                >
                  <Mail className="w-4 h-4" />
                  <span>Contact Us</span>
                </a>
              </div>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  )
}

export default About