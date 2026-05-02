# Insurance ChatBot - Deployment & Setup Guide

## Overview

This is a production-ready insurance chatbot application built with:
- **Backend**: FastAPI with LangChain RAG
- **Frontend**: Angular 
- **LLM**: Free Ollama (Mistral) - no API keys needed
- **Embeddings**: Sentence Transformers (free)
- **Vector DB**: Chroma
- **Caching**: Redis
- **Deployment**: Docker & Kubernetes

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend)
- Kubernetes cluster (for k8s deployment)

### 2. Docker Compose (Local Development)

```bash
cd /path/to/allianzgpt

# Copy environment files
cp backend/.env.example backend/.env
cp ingest_service/.env.example ingest_service/.env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

**Services will be available at:**
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- Ingest Service: http://localhost:8001
- API Docs: http://localhost:8000/docs
- Chroma Vector DB: http://localhost:8002
- Ollama LLM: http://localhost:11434

### 3. Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Start Ollama in Docker first
docker run -d -p 11434:11434 ollama/ollama

# Download model (one-time)
# In Docker container: ollama pull mistral

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint in environment.ts
# Update: apiUrl: 'http://localhost:8000'

# Start development server
npm start

# Access at http://localhost:4200
```

### 4. Kubernetes Deployment

#### Prerequisites
```bash
# Install kubectl
# Install Docker
# Have access to a Kubernetes cluster (minikube, EKS, GKE, etc.)
```

#### Deploy to Kubernetes

```bash
# Navigate to kubernetes directory
cd kubernetes

# Create namespace and config
kubectl apply -f 00-namespace-config.yaml

# Deploy services in order
kubectl apply -f 01-ollama.yaml
kubectl apply -f 02-redis.yaml
kubectl apply -f 03-backend.yaml
kubectl apply -f 04-ingest.yaml
kubectl apply -f 05-frontend.yaml
kubectl apply -f 06-rbac-network-policy.yaml

# Check deployment status
kubectl get pods -n insurance-chatbot

# View logs
kubectl logs -n insurance-chatbot deployment/backend -f

# Port forward to test locally
kubectl port-forward -n insurance-chatbot svc/backend 8000:8000
kubectl port-forward -n insurance-chatbot svc/frontend 4200:80

# Access at:
# Frontend: http://localhost:4200
# Backend: http://localhost:8000
```

#### Scaling

```bash
# Manually scale backend
kubectl scale deployment backend -n insurance-chatbot --replicas=3

# HPA will automatically scale based on CPU/memory
# Min: 2, Max: 5 replicas for backend
```

### 5. API Usage

#### Authentication

```bash
# Login to get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "AllianzTest123!"
  }'

# Response:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLC...",
#   "token_type": "bearer",
#   "expires_in": 7200
# }
```

#### Ingest Documents

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "insurance",
    "documents": [
      "Your health insurance policy covers preventive care at no cost..."
    ],
    "insurance_type": "health"
  }'
```

#### Query Knowledge Base

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is covered under my health insurance?",
    "top_k": 5
  }'
```

#### Stream Query Results

```bash
curl -N http://localhost:8000/api/query/stream?q=insurance%20coverage \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Configuration

#### LLM Models

Default: **Ollama with Mistral** (free, lightweight, ~7B parameters)

To use other models:

```bash
# In docker-compose or .env:

# Option 1: Different Ollama models
OLLAMA_MODEL=neural-chat  # Faster, smaller
OLLAMA_MODEL=llama2       # More capable, larger

# Option 2: OpenAI (requires API key)
LLM_TYPE=openai
OPENAI_API_KEY=your_key

# Option 3: HuggingFace
LLM_TYPE=huggingface
HUGGINGFACE_MODEL_NAME=mistralai/Mistral-7B-v0.1
```

#### Embedding Models

Default: **Sentence Transformers - all-MiniLM-L6-v2** (free, fast)

Available options:
- `all-MiniLM-L6-v2` - Fast, small (12M)
- `all-mpnet-base-v2` - Slow, better quality (109M)
- `all-distilroberta-v1` - Very fast (27M)

### 7. Monitoring & Troubleshooting

#### Check Service Health

```bash
# All services
curl http://localhost:8000/api/health

# Response includes:
# - Vector store status
# - LLM model availability
# - Document count
```

#### View Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f ingest

# Kubernetes
kubectl logs -n insurance-chatbot deployment/backend -f
kubectl logs -n insurance-chatbot deployment/ollama -f
```

#### Common Issues

**Ollama not responding:**
```bash
# Restart Ollama service
docker-compose restart ollama

# Or pull model again
docker exec insurance-ollama ollama pull mistral
```

**Out of memory:**
```bash
# Reduce model size in docker-compose.yml
# Change OLLAMA_MODEL to a smaller model
```

**Slow responses:**
```bash
# Check vector store size
# Optimize chunk size and overlap in .env
CHUNK_SIZE=300
CHUNK_OVERLAP=50
```

### 8. Insurance Domain Features

- **Policy Analysis**: Extract and search insurance policies
- **Claim Support**: Help customers understand claim procedures
- **Coverage Lookup**: Find coverage details from policy documents
- **Multilingual Support**: Can be extended to multiple languages
- **Document Validation**: Validates insurance documents on upload
- **Audit Trail**: Logs all queries and responses for compliance

### 9. Security Features

- JWT authentication with strong password requirements
- Role-based access control (RBAC) in Kubernetes
- Network policies for inter-service communication
- Security headers (HSTS, X-Frame-Options, etc.)
- SSL/TLS ready (add cert-manager for auto-renewal)
- Pod security policies and non-root containers

### 10. Production Checklist

- [ ] Change JWT_SECRET to a strong random value
- [ ] Update CORS_ORIGINS to your domains
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure logging aggregation (ELK, Loki)
- [ ] Set up backup for vector database
- [ ] Configure ingress controller
- [ ] Enable network policies
- [ ] Set resource quotas
- [ ] Configure pod autoscaling
- [ ] Test disaster recovery
- [ ] Load testing and optimization

### 11. Maintenance

#### Update Models

```bash
# Pull new Ollama model
docker exec insurance-ollama ollama pull mistral:latest

# Update embedding model
# Edit .env: EMBEDDING_MODEL=all-mpnet-base-v2
docker-compose restart backend
```

#### Backup Vector Store

```bash
# Backup Chroma data
docker cp insurance-ollama:/app/.chroma_data ./backup/

# Or use Kubernetes backup tools
```

### 12. Performance Optimization

- Use Sentence Transformers cache layer (Redis)
- Batch document ingestion
- Use smaller chunks for faster retrieval
- Implement result caching
- Use CDN for frontend assets
- Configure GPU acceleration for Ollama (if available)

### 13. Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Ollama Models**: https://ollama.ai/library
- **LangChain Docs**: https://python.langchain.com/

## Architecture Diagram

```
┌─────────────┐
│  Frontend   │ (Angular, Port 4200)
│  (Nginx)    │
└──────┬──────┘
       │ HTTP/WebSocket
┌──────┴──────────────┐
│   Backend API       │ (FastAPI, Port 8000)
│ - Authentication    │
│ - RAG Engine        │
│ - Query Processing  │
└──────┬──────────────┘
       │
    ┌──┴──┬──────┬───────┐
    │     │      │       │
    ▼     ▼      ▼       ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌─────────┐
│Ollama  │ │Chroma  │ │ Redis  │ │ Ingest  │
│(LLM)   │ │(Vector)│ │(Cache) │ │Service  │
└────────┘ └────────┘ └────────┘ └─────────┘
```

## License

MIT License - See LICENSE file for details
