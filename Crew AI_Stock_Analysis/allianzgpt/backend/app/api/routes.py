import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from typing import Generator

from app.models.schemas import LoginRequest, TokenResponse, IngestRequest, QueryRequest, QueryResponse
from app.services.auth import create_access_token, verify_token
from app.services.vectorstore import VectorStoreService
from app.services.rag import RAGService
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Simple in-memory user store for demo; replace with LDAP, DB, or SSO in prod.
USERS = {
    "alice": {"username": "alice", "password": "Allianz123"},
    "bob": {"username": "bob", "password": "Allianz456"},
}

vector_service = VectorStoreService()
rag_service = RAGService(vector_service)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        username = verify_token(token)
        if username not in USERS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return USERS[username]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.app_name}


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = USERS.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/ingest")
async def ingest(payload: IngestRequest, user: dict = Depends(get_current_user)):
    if not payload.documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    vectordoc_ids = [str(uuid.uuid4()) for _ in payload.documents]
    vector_service.add_documents(payload.documents, metadatas=[{"id": doc_id, "user": user["username"]} for doc_id in vectordoc_ids], namespace=payload.namespace)

    return {"status": "ingested", "documents": len(payload.documents), "namespace": payload.namespace}


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest, user: dict = Depends(get_current_user)):
    result = rag_service.answer(payload.query)
    return QueryResponse(answer=result["answer"], source_documents=result["sources"])


def stream_generator(query: str) -> Generator[str, None, None]:
    # Minimal token-style stream from OpenAI
    data = rag_service.answer(query)
    for chunk in [data["answer"][i : i + 80] for i in range(0, len(data["answer"]), 80)]:
        yield f"data: {chunk}\n\n"


@router.get("/query/stream")
async def query_stream(q: str, user: dict = Depends(get_current_user)):
    return StreamingResponse(stream_generator(q), media_type="text/event-stream")


@router.websocket("/ws/query")
async def websocket_query(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            query_text = data.get("query")
            if not query_text:
                await ws.send_json({"error": "Missing query"})
                continue

            answer_payload = rag_service.answer(query_text)
            chunk_size = 80
            for i in range(0, len(answer_payload["answer"]), chunk_size):
                await ws.send_json({"delta": answer_payload["answer"][i : i + chunk_size]})
            await ws.send_json({"done": True, "sources": answer_payload["sources"]})
    except Exception:
        await ws.close()
