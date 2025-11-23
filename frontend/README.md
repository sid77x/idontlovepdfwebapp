# I Don't Love PDF - Frontend

A modern, responsive React frontend for the I Don't Love PDF toolkit.

## Features

- 🎨 Modern UI with Tailwind CSS
- 📱 Fully responsive design
- 🔄 Real-time processing queue
- 📊 Progress tracking
- 🎭 Smooth animations with Framer Motion
- 🛡️ Client-side file processing
- 📁 Drag & drop file uploads
- 🎯 10+ PDF tools available

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Available Tools

- ✅ **Merge PDFs** - Combine multiple PDF files
- ✅ **Rotate PDF** - Rotate pages in PDF documents
- ✅ **Split PDF** - Extract or split PDF pages
- ✅ **Protect PDF** - Add password protection
- ✅ **Compress PDF** - Reduce file size
- ✅ **Watermark PDF** - Add text/image watermarks
- ✅ **OCR PDF** - Extract text from scanned documents
- ✅ **PDF to Images** - Convert PDF pages to images
- ✅ **Images to PDF** - Convert images to PDF
- ✅ **HTML to PDF** - Convert HTML to PDF

## Architecture

The frontend is built with:

- **React 18** - Modern React with hooks and concurrent features
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication
- **React Dropzone** - Drag & drop file uploads
- **Lucide React** - Beautiful SVG icons

## API Integration

The frontend communicates with the microservices backend through:

- **Base URL:** `http://localhost:8000` (configurable via `.env`)
- **Proxy Setup:** Vite dev server proxies `/api` requests
- **File Uploads:** Multipart form data with progress tracking
- **Error Handling:** Comprehensive error messages and retry logic

## Development

### Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── FileUpload.jsx   # Drag & drop file upload
│   ├── Navbar.jsx       # Navigation bar
│   ├── ProcessingQueue.jsx # Real-time job queue
│   ├── ToolGrid.jsx     # Tool selection grid
│   └── ToolModal.jsx    # Tool configuration modal
├── contexts/            # React contexts
│   └── ProcessingContext.jsx # Global processing state
├── pages/               # Page components
│   ├── Home.jsx         # Landing page
│   ├── Tools.jsx        # Tools page
│   └── About.jsx        # About page
├── services/            # API services
│   └── api.js           # Backend API integration
├── App.jsx              # Main app component
├── main.jsx             # App entry point
└── index.css            # Global styles
```

### Environment Variables

Create a `.env` file:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Adding New Tools

1. **Add tool definition** to `src/components/ToolGrid.jsx`
2. **Add API method** to `src/services/api.js`
3. **Add tool options** to `src/components/ToolModal.jsx`
4. **Update processing logic** in the modal component

## Deployment

### Production Build

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

### Static Hosting

The frontend can be deployed to any static hosting service:

- **Vercel:** `vercel --prod`
- **Netlify:** Drag & drop the `dist` folder
- **GitHub Pages:** Push to `gh-pages` branch
- **AWS S3:** Upload `dist` contents to S3 bucket

### Docker Deployment

```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- **Lazy Loading:** Components loaded on demand
- **Code Splitting:** Automatic route-based splitting
- **Asset Optimization:** Images and fonts optimized
- **Bundle Size:** ~300KB gzipped

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details