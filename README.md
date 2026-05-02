# Insurance ChatBot - RAG-Based LLM Application

A production-ready insurance chatbot built with **LangChain**, **RAG (Retrieval Augmented Generation)**, and **free LLM models**. Features comprehensive validation, Docker & Kubernetes deployment support, and enterprise-grade security.

![Architecture](docs/architecture.png)

## 🚀 Features

- **Free LLM Models**: Uses Ollama with Mistral (no API keys required)
- **RAG System**: Retrieves relevant insurance documents before generating answers
- **Vector Database**: Chroma for efficient document storage and retrieval
- **Sentence Transformers**: Free embeddings model
- **Authentication**: JWT-based with strong password validation
- **Real-time Streaming**: SSE and WebSocket support for chat streams
- **Redis Caching**: Performance optimization
- **Docker & Kubernetes Ready**: Production deployment configurations included
- **Comprehensive Validation**: All inputs validated with Pydantic
- **Insurance Domain**: Pre-loaded with health, property, auto, and life insurance data
- **Horizontal Scaling**: HPA configured for auto-scaling based on load
- **Network Policies**: Kubernetes network segmentation
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend)
- At least 8GB RAM
- 50GB disk space (for Ollama models and vector database)

## 🏃 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
cd allianzgpt

# Windows: Run quickstart
quickstart.bat

# macOS/Linux: Run quickstart
bash quickstart.sh

# Or manually:
cp backend/.env.example backend/.env
cp ingest_service/.env.example ingest_service/.env
docker-compose up -d
```

**Services will be available at:**
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ingest Service**: http://localhost:8001

### Default Credentials

```
Username: alice
Password: AllianzTest123!
```

## 📦 Project Structure

```
allianzgpt/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/routes.py            # API endpoints
│   │   ├── core/config.py           # Configuration management
│   │   ├── data/insurance_samples.py # Insurance knowledge base
│   │   ├── models/schemas.py        # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── auth.py              # Authentication & password validation
│   │   │   ├── rag.py               # RAG service with LLM
│   │   │   ├── vectorstore.py       # Vector store management
│   │   │   └── seeder.py            # Data seeding utility
│   │   └── main.py                  # FastAPI app initialization
│   ├── Dockerfile                   # Backend Docker image
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Configuration template
│
├── frontend/                         # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── chat/                # Chat component
│   │   │   └── services/api.service.ts # API client
│   │   └── environments/environment.ts
│   ├── Dockerfile                   # Frontend Docker image
│   ├── nginx.conf                   # Nginx configuration
│   └── package.json
│
├── ingest_service/                   # Document ingestion service
│   ├── app/main.py                  # Ingest API
│   ├── Dockerfile                   # Ingest service Docker image
│   ├── requirements.txt             # Dependencies
│   └── .env.example                 # Configuration template
│
├── kubernetes/                       # Kubernetes manifests
│   ├── 00-namespace-config.yaml     # Namespace and config
│   ├── 01-ollama.yaml               # Ollama LLM deployment
│   ├── 02-redis.yaml                # Redis deployment
│   ├── 03-backend.yaml              # Backend deployment with HPA
│   ├── 04-ingest.yaml               # Ingest service deployment
│   ├── 05-frontend.yaml             # Frontend deployment
│   └── 06-rbac-network-policy.yaml  # RBAC and network policies
│
├── docker-compose.yml               # Docker Compose orchestration
├── DEPLOYMENT.md                    # Deployment guide
├── quickstart.sh                    # Quick start script (Linux/macOS)
├── quickstart.bat                   # Quick start script (Windows)
└── README.md                        # This file
```

## 🔧 Configuration

### Environment Variables

See `backend/.env.example` for full configuration options:

```bash
# LLM Configuration
LLM_TYPE=ollama              # ollama, openai, huggingface
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral         # Other options: neural-chat, llama2

# Embeddings
EMBEDDING_TYPE=sentence-transformer
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Vector Database
VECTOR_DB_TYPE=chroma
CHROMA_PERSIST_DIR=./.chroma_data

# RAG
RAG_TOP_K=5                  # Number of documents to retrieve
RAG_SIMILARITY_THRESHOLD=0.5

# Security
JWT_SECRET=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## 📚 API Endpoints

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "AllianzTest123!"
  }'

# Register (new user)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

### Document Ingestion

```bash
# Ingest insurance documents
curl -X POST http://localhost:8000/api/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "insurance",
    "documents": [
      "Health insurance covers preventive care...",
      "Your policy includes coverage for..."
    ],
    "insurance_type": "health"
  }'
```

### Query Knowledge Base

```bash
# Query with response
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is covered under my health insurance?",
    "top_k": 5
  }'

# Stream query results
curl -N http://localhost:8000/api/query/stream?q=insurance%20coverage \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### WebSocket (Real-time Chat)

```javascript
// JavaScript example
const ws = new WebSocket('ws://localhost:8000/api/ws/query');

ws.onopen = () => {
  ws.send(JSON.stringify({
    query: "What insurance policies do you offer?"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

## 🐳 Docker Deployment

### Building Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
docker-compose build ingest
```

### Running Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# View specific service logs
docker-compose logs -f ollama

# Scale a service
docker-compose up -d --scale ingest=3

# Stop services
docker-compose down

# Clean everything
docker-compose down -v
```

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
# Have access to a Kubernetes cluster
# Have docker images built and pushed to registry
```

### Deploy to Kubernetes

```bash
# Create namespace and config
kubectl apply -f kubernetes/00-namespace-config.yaml

# Deploy services in order
kubectl apply -f kubernetes/01-ollama.yaml
kubectl apply -f kubernetes/02-redis.yaml
kubectl apply -f kubernetes/03-backend.yaml
kubectl apply -f kubernetes/04-ingest.yaml
kubectl apply -f kubernetes/05-frontend.yaml
kubectl apply -f kubernetes/06-rbac-network-policy.yaml

# Check status
kubectl get pods -n insurance-chatbot
kubectl get svc -n insurance-chatbot
kubectl get hpa -n insurance-chatbot

# View logs
kubectl logs -n insurance-chatbot deployment/backend -f

# Port forward to local machine
kubectl port-forward -n insurance-chatbot svc/backend 8000:8000
kubectl port-forward -n insurance-chatbot svc/frontend 4200:80

# Clean up
kubectl delete namespace insurance-chatbot
```

### Scaling

```bash
# Auto-scaling is configured via HPA
# View current scaling state
kubectl get hpa -n insurance-chatbot

# Manually scale
kubectl scale deployment backend -n insurance-chatbot --replicas=5

# View scaling events
kubectl describe hpa backend-hpa -n insurance-chatbot
```

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Validation**: Strong password requirements (8+ chars, uppercase, digit, special char)
- **HTTPS Ready**: TLS/SSL support via Ingress
- **Network Policies**: Kubernetes network segmentation
- **RBAC**: Role-based access control
- **Security Headers**: HSTS, X-Frame-Options, X-XSS-Protection
- **Rate Limiting**: 100 requests per hour per user
- **Non-root Containers**: Security best practices

## 🧪 Testing & Development

### Run Locally

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start services (Redis, Ollama)
docker run -d -p 6379:6379 redis:7-alpine
docker run -d -p 11434:11434 ollama/ollama

# Run backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Update API URL in environment.ts
# apiUrl: 'http://localhost:8000'

# Start dev server
npm start

# Access at http://localhost:4200
```

### API Testing

```bash
# Using curl
curl -X GET http://localhost:8000/api/health

# Using Python requests
python -c "
import requests
resp = requests.get('http://localhost:8000/api/health')
print(resp.json())
"

# Using Swagger UI
# Visit http://localhost:8000/docs
```

## 🔌 LLM Model Options

### Ollama (Default - Recommended)

- **Model**: Mistral 7B (default, free, lightweight)
- **Alternatives**:
  - `neural-chat` - Faster responses
  - `llama2` - Better quality, larger
  - `phi` - Very small, ultra-fast

```bash
# Pull different model
docker exec insurance-ollama ollama pull neural-chat
# Update .env: OLLAMA_MODEL=neural-chat
```

### OpenAI

```bash
# Set in .env
LLM_TYPE=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

### HuggingFace

```bash
# Set in .env
LLM_TYPE=huggingface
HUGGINGFACE_MODEL_NAME=mistralai/Mistral-7B-v0.1
HUGGINGFACE_API_TOKEN=hf_...
```

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Response includes:
{
  "status": "healthy",
  "service": "Insurance ChatBot API",
  "version": "1.0.0",
  "components": {
    "vector_store": "operational",
    "llm": "ollama",
    "documents": 10
  }
}
```

### Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f ollama

# Kubernetes
kubectl logs -n insurance-chatbot deployment/backend -f
```

## 🚀 Performance Optimization

- **Caching**: Redis caches embeddings and frequent queries
- **Batching**: Batch document ingestion for better throughput
- **Chunking**: Configurable document chunk sizes
- **GPU Support**: Optional CUDA support for Ollama (requires GPU)
- **Load Balancing**: Multiple replicas with HPA

## 📝 Validation & Error Handling

### Request Validation

All endpoints validate input with Pydantic:

```python
# Example: Query validation
- query: 1-2000 characters
- top_k: 1-20 results
- namespace: required
- include_metadata: optional boolean
```

### Error Responses

```json
{
  "status": "error",
  "detail": "Descriptive error message",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔄 Insurance Domain Features

### Pre-loaded Insurance Data

The system comes with sample data for:
- **Health Insurance**: Coverage types, deductibles, exclusions
- **Property Insurance**: Dwelling coverage, liability, exclusions
- **Auto Insurance**: Liability, collision, comprehensive coverage
- **Life Insurance**: Terms, underwriting, claims process

### Custom Insurance Data

```bash
# Ingest custom insurance documents
curl -X POST http://localhost:8000/api/ingest \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "insurance",
    "documents": ["Your policy text here..."],
    "metadata": [{
      "insurance_type": "health",
      "policy_number": "POL-123456",
      "effective_date": "2024-01-01"
    }]
  }'
```

## 🐛 Troubleshooting

### Ollama Not Responding

```bash
# Restart Ollama
docker-compose restart ollama

# Check Ollama logs
docker-compose logs ollama

# Manually pull model
docker exec insurance-ollama ollama pull mistral
```

### Out of Memory

```bash
# Reduce model size in docker-compose.yml
OLLAMA_MODEL=neural-chat  # Smaller model

# Increase Docker memory limit
# Edit docker-compose.yml: mem_limit: 8g
```

### Slow Queries

```bash
# Reduce chunk size in .env
CHUNK_SIZE=300
CHUNK_OVERLAP=25

# Reduce RAG_TOP_K
RAG_TOP_K=3

# Check Redis is running
docker-compose logs redis
```

### Vector Store Issues

```bash
# Clear vector store
docker exec insurance-backend rm -rf /app/.chroma_data

# Restart backend to reseed
docker-compose restart backend
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [LangChain Docs](https://python.langchain.com/)
- [Ollama Models](https://ollama.ai/library)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom model fine-tuning
- [ ] GraphQL API
- [ ] Mobile app
- [ ] Voice input support
- [ ] Callback integration with insurance systems
- [ ] Advanced RBAC with database
- [ ] Document management UI
- [ ] Audit logging

## 👥 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: support@insurance-chatbot.com
- Documentation: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready
