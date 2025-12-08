#!/bin/bash

echo "🚀 Starting Alert System Demo with Django LiveView"
echo "=================================================="
echo ""

# Build and start containers
echo "📦 Building and starting Docker containers..."
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if containers are running
if docker compose ps | grep -q "Up"; then
    echo "✅ All services are running!"
    echo ""
    echo "🌐 Application is available at: http://localhost:8000"
    echo ""
    echo "📝 To view logs, run: docker compose logs -f web"
    echo "🛑 To stop, run: docker compose down"
    echo ""
    echo "Features available:"
    echo "  • View all alerts in a table"
    echo "  • Create random alerts"
    echo "  • Delete alerts"
    echo "  • View alert details in a modal"
    echo "  • Create new alerts with form validation"
    echo "  • Real-time broadcast notifications"
    echo ""
else
    echo "❌ Error: Some services failed to start"
    echo "Run 'docker compose logs' to see what went wrong"
    exit 1
fi
