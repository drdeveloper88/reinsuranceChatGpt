# AllianzGPT Microservices Reference

This repository demonstrates a secure internal AI platform architecture similar to the AllianzGPT narrative. It includes:

- Backend (FastAPI) with LangChain, OpenAI embeddings, and Chroma vector store (RAG) in `backend/`
- Ingest service (FastAPI) in `ingest_service/` for document upload pipelines
- Frontend (Angular) in `frontend/` with real-time SSE streaming and token-based auth

## Backend setup

1. python -m venv .venv
2. .venv\Scripts\activate
3. pip install -r backend/requirements.txt
4. copy backend/.env.example backend/.env and set keys
5. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Ingest service setup

1. activate venv
2. pip install -r ingest_service/requirements.txt
3. set BACKEND_INGEST_URL=http://localhost:8000/api/ingest
4. uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

## Frontend setup

1. cd frontend
2. npm install
3. npm start

## Security & Design

- JWT auth in backend
- CORS restricted to frontend origin
- Vector store persisted in Chroma local store
- Query path uses retrieval + grounding and stream tokens for real-time UX
- Ingest service is microservice decoupled from query service
- For enterprise, adopt SSO (Azure AD), RBAC, logging, monitoring, and Secure AI governance

## Notes

This implementation is a blueprint. Production deployment should include:
- Kubernetes with mutual TLS
- Vault for secrets
- Structured observability (OpenTelemetry)
- Labeling training data for bias mitigation
- retriever caching, vector DB shards, dataset refresh flows
