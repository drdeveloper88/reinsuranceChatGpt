#!/bin/bash

# Insurance ChatBot - Quick Start Script

set -e

echo "================================================"
echo "Insurance ChatBot - Quick Start"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Copy environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "Creating backend .env file..."
    cp backend/.env.example backend/.env
fi

if [ ! -f ingest_service/.env ]; then
    echo "Creating ingest service .env file..."
    cp ingest_service/.env.example ingest_service/.env
fi

echo ""
echo "Starting services..."
echo "This may take a few minutes on first run..."
echo ""

# Start services
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check backend
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✓ Backend API is running (http://localhost:8000)"
else
    echo "✗ Backend API not responding yet, giving it more time..."
    sleep 5
fi

# Check ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama LLM is running (http://localhost:11434)"
else
    echo "✗ Ollama not responding yet"
fi

echo ""
echo "================================================"
echo "Services are starting up!"
echo "================================================"
echo ""
echo "Access the application at:"
echo "  Frontend:         http://localhost:4200"
echo "  Backend API:      http://localhost:8000"
echo "  API Docs:         http://localhost:8000/docs"
echo "  Ingest Service:   http://localhost:8001"
echo "  Redis:            localhost:6379"
echo "  Ollama:           http://localhost:11434"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f backend"
echo "  Stop services:    docker-compose down"
echo "  Rebuild images:   docker-compose up --build"
echo ""
echo "Default login credentials:"
echo "  Username: alice"
echo "  Password: AllianzTest123!"
echo ""
echo "First run note: Ollama may take a minute to download the model."
echo "Check logs: docker-compose logs -f ollama"
echo ""
echo "================================================"
