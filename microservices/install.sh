#!/bin/bash
# Install PDF Microservices Dependencies (Linux/Mac)

echo "Installing PDF Microservices Dependencies..."
echo "============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and add it to your PATH"
    exit 1
fi

echo "Python found. Installing dependencies..."

# Install requirements
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "================================"
echo "Dependencies installed successfully!"
echo ""
echo "To start the microservices, run:"
echo "  python3 start_services.py"
echo ""
echo "Or run individual services:"
echo "  cd services"
echo "  python3 merge_service.py"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs  (Orchestrator)"
echo "  http://localhost:8001/docs  (Merge Service)"
echo "  http://localhost:8002/docs  (Rotate Service)"
echo "  http://localhost:8003/docs  (Split Service)"
echo "================================"