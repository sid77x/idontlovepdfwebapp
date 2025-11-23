#!/bin/bash

# IdontLovePDF Docker Startup Script
# This script helps you start the application using Docker

set -e

echo "🐳 IdontLovePDF Docker Startup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Determine which docker-compose command to use
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

# Parse command line arguments
MODE="${1:-production}"

case "$MODE" in
    production|prod)
        echo "🚀 Starting in PRODUCTION mode..."
        echo ""
        $COMPOSE_CMD up -d
        ;;
    development|dev)
        echo "🔧 Starting in DEVELOPMENT mode..."
        echo ""
        $COMPOSE_CMD -f docker-compose.dev.yml up
        ;;
    build)
        echo "🔨 Building Docker images..."
        echo ""
        $COMPOSE_CMD build --no-cache
        ;;
    stop)
        echo "🛑 Stopping all services..."
        echo ""
        $COMPOSE_CMD down
        ;;
    restart)
        echo "🔄 Restarting all services..."
        echo ""
        $COMPOSE_CMD restart
        ;;
    logs)
        echo "📋 Showing logs..."
        echo ""
        $COMPOSE_CMD logs -f
        ;;
    status)
        echo "📊 Service status:"
        echo ""
        $COMPOSE_CMD ps
        ;;
    clean)
        echo "🧹 Cleaning up (removing containers, volumes, and images)..."
        echo ""
        $COMPOSE_CMD down -v --rmi all
        ;;
    help|--help|-h)
        echo "Usage: ./docker-start.sh [command]"
        echo ""
        echo "Commands:"
        echo "  production, prod    Start in production mode (default)"
        echo "  development, dev    Start in development mode with hot-reload"
        echo "  build               Rebuild all Docker images"
        echo "  stop                Stop all services"
        echo "  restart             Restart all services"
        echo "  logs                Show and follow logs"
        echo "  status              Show service status"
        echo "  clean               Remove all containers, volumes, and images"
        echo "  help                Show this help message"
        echo ""
        exit 0
        ;;
    *)
        echo "❌ Unknown command: $MODE"
        echo "Run './docker-start.sh help' for usage information"
        exit 1
        ;;
esac

# Show access URLs if services are being started
case "$MODE" in
    production|prod|development|dev)
        echo ""
        echo "✅ Services are starting..."
        echo ""
        echo "📱 Access the application at:"
        echo "   • Streamlit App:      http://localhost:8501"
        echo "   • Microservices API:  http://localhost:8000"
        echo "   • API Documentation:  http://localhost:8000/docs"
        echo "   • React Frontend:     http://localhost:3000"
        echo ""
        echo "📊 Check service status: ./docker-start.sh status"
        echo "📋 View logs:            ./docker-start.sh logs"
        echo "🛑 Stop services:        ./docker-start.sh stop"
        echo ""
        ;;
esac

exit 0
