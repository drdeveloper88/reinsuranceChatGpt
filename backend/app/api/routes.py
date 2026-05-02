import json
import uuid
import logging
import time
from datetime import datetime, timedelta
from typing import Generator, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, Query, Header
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder

from app.models.schemas import (
    LoginRequest, TokenResponse, IngestRequest, IngestResponse,
    QueryRequest, QueryResponse, UserRegister, UserResponse,
    StreamingChunk, DocumentCollection, ErrorDetail, HealthCheckResponse,
    DeleteDocumentsRequest, SourceDocument
)
from app.services.auth import TokenManager, PasswordManager, PasswordValidator
from app.services.vectorstore import VectorStoreService
from app.services.rag import RAGService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# In-memory user store (replace with DB in production)
USERS = {
    "alice": {
        "user_id": "1",
        "username": "alice",
        "password_hash": PasswordManager.hash_password("AllianzTest123!"),
        "email": "alice@insurance.com",
        "full_name": "Alice Smith",
        "created_at": datetime.utcnow(),
        "role": "admin"
    },
    "bob": {
        "user_id": "2",
        "username": "bob",
        "password_hash": PasswordManager.hash_password("BobTest456!"),
        "email": "bob@insurance.com",
        "full_name": "Bob Johnson",
        "created_at": datetime.utcnow(),
        "role": "user"
    },
}

# Initialize services
vector_service = VectorStoreService()
rag_service = RAGService(vector_service)

# Rate limiting
request_count = {}


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    try:
        username = TokenManager.verify_token(token)
        if username not in USERS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return USERS[username]
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _apply_rate_limit(username: str) -> None:
    """Simple rate limiting (100 requests per hour)"""
    now = time.time()
    if username not in request_count:
        request_count[username] = []
    request_count[username] = [t for t in request_count[username] if now - t < 3600]
    if len(request_count[username]) >= 100:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 100 requests per hour.",
        )
    request_count[username].append(now)


def check_rate_limit(user: dict = Depends(get_current_user)):
    """Simple rate limiting (100 requests per hour)"""
    _apply_rate_limit(user["username"])
    return user


def extract_sse_token(
    access_token: Optional[str] = Query(
        None, description="JWT for SSE/EventSource clients (no Authorization header)"
    ),
    authorization: Optional[str] = Header(None),
) -> str:
    """Bearer header or access_token query param (required for browser EventSource)."""
    if access_token:
        return access_token.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user_sse(token: str = Depends(extract_sse_token)):
    """Authenticate SSE/stream clients using header or query token."""
    try:
        username = TokenManager.verify_token(token)
        if username not in USERS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return USERS[username]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSE authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_rate_limit_sse(user: dict = Depends(get_current_user_sse)):
    _apply_rate_limit(user["username"])
    return user


# ==================== Health & Status ====================
@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        stats = vector_service.get_collection_stats()
        return HealthCheckResponse(
            status="healthy",
            service=settings.app_name,
            version="1.0.0",
            timestamp=datetime.utcnow(),
            components={
                "vector_store": "operational",
                "llm": str(settings.llm_type),
                "documents": str(stats.get("total_documents", 0))
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# ==================== Authentication ====================
@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        user = USERS.get(payload.username)
        if not user:
            logger.warning(f"Failed login attempt for non-existent user: {payload.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        if not PasswordManager.verify_password(payload.password, user["password_hash"]):
            logger.warning(f"Failed login attempt for user: {payload.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Generate token
        access_token = TokenManager.create_access_token(
            data={"sub": user["username"]},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        logger.info(f"User authenticated: {user['username']}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/auth/register", response_model=UserResponse)
async def register(payload: UserRegister):
    """Register new user"""
    try:
        # Check if user exists
        if payload.username in USERS:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Validate password strength
        is_valid, error_msg = PasswordValidator.validate(payload.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create user
        new_user = {
            "user_id": str(uuid.uuid4()),
            "username": payload.username.lower(),
            "password_hash": PasswordManager.hash_password(payload.password),
            "email": payload.email.lower(),
            "full_name": payload.full_name,
            "created_at": datetime.utcnow(),
            "role": "user"
        }
        
        USERS[payload.username.lower()] = new_user
        logger.info(f"New user registered: {payload.username}")
        
        return UserResponse(
            user_id=new_user["user_id"],
            username=new_user["username"],
            email=new_user["email"],
            full_name=new_user["full_name"],
            created_at=new_user["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


# ==================== Document Ingestion ====================
@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    payload: IngestRequest,
    user: dict = Depends(check_rate_limit)
):
    """Ingest insurance documents into vector store"""
    start_time = time.time()
    try:
        if not payload.documents:
            raise HTTPException(status_code=400, detail="No documents provided")
        
        # Generate document IDs
        doc_ids = [str(uuid.uuid4()) for _ in payload.documents]
        
        # Prepare metadata
        metadatas = []
        for i, doc_id in enumerate(doc_ids):
            metadata = {
                "id": doc_id,
                "user": user["username"],
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Add custom metadata if provided
            if payload.metadata and i < len(payload.metadata):
                custom_meta = payload.metadata[i].dict(exclude_none=True)
                metadata.update(custom_meta)
            
            metadatas.append(metadata)
        
        # Ingest documents
        vector_service.add_documents(
            payload.documents,
            metadatas=metadatas,
            namespace=payload.namespace
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Ingested {len(payload.documents)} documents for user {user['username']}")
        
        return IngestResponse(
            status="success",
            documents_ingested=len(payload.documents),
            failed_documents=0,
            namespace=payload.namespace,
            document_ids=doc_ids,
            warnings=None,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")


# ==================== Query & RAG ====================
@router.post("/query", response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    user: dict = Depends(check_rate_limit)
):
    """Query insurance knowledge base using RAG"""
    start_time = time.time()
    try:
        if not payload.query or not payload.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Generate answer
        result = rag_service.answer(payload.query, namespace=payload.namespace)
        
        processing_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            answer=result["answer"],
            source_documents=[
                SourceDocument(**doc) for doc in result["sources"]
            ],
            confidence_score=result["confidence_score"],
            processing_time_ms=processing_time,
            model_used=result["model_used"],
            timestamp=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.get("/query/stream")
async def query_stream(
    q: str = Query(..., min_length=1, max_length=2000),
    user: dict = Depends(check_rate_limit_sse),
):
    """Stream query results (SSE). Uses check_rate_limit_sse so JWT can be passed as access_token."""

    def stream_generator() -> Generator:
        try:
            for chunk in rag_service.stream_answer(q):
                yield f"data: {json.dumps(jsonable_encoder(chunk))}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield "data: " + json.dumps({"type": "error", "error": str(e)}) + "\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@router.websocket("/ws/query")
async def websocket_query(ws: WebSocket):
    """WebSocket endpoint for real-time query streaming"""
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            query_text = data.get("query")
            namespace = data.get("namespace", "insurance")
            
            if not query_text:
                await ws.send_json({"error": "Missing query", "timestamp": datetime.utcnow().isoformat()})
                continue
            
            # Generate answer
            answer_data = rag_service.answer(query_text, namespace=namespace)
            
            # Stream chunks
            for chunk in rag_service.stream_answer(query_text, namespace=namespace):
                await ws.send_json({
                    **chunk,
                    "timestamp": datetime.utcnow().isoformat()
                })
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await ws.close(code=1000, reason=str(e))


# ==================== Document Management ====================
@router.delete("/documents")
async def delete_documents(
    payload: DeleteDocumentsRequest,
    user: dict = Depends(get_current_user)
):
    """Delete documents"""
    try:
        if payload.document_ids:
            vector_service.delete_documents(payload.document_ids)
            count = len(payload.document_ids)
        elif payload.namespace:
            vector_service.clear_namespace(payload.namespace)
            count = 0  # Actual count from backend
        else:
            raise HTTPException(status_code=400, detail="No deletion parameters provided")
        
        logger.info(f"User {user['username']} deleted documents")
        
        return {
            "status": "success",
            "message": f"Deleted {count} documents" if payload.document_ids else f"Cleared namespace {payload.namespace}",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/collections", response_model=list[DocumentCollection])
async def get_collections(user: dict = Depends(get_current_user)):
    """List document collections"""
    try:
        # This is a simplified implementation
        stats = vector_service.get_collection_stats()
        return [
            DocumentCollection(
                collection_id="default",
                name="Insurance Knowledge Base",
                description="Main insurance documentation collection",
                document_count=stats.get("total_documents", 0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                insurance_types=["health", "property", "auto", "life"]
            )
        ]
    except Exception as e:
        logger.error(f"Get collections error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve collections")


# ==================== Root ====================
@router.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": f"{settings.app_name} is live",
        "version": "1.0.0",
        "llm_model": str(settings.llm_type),
        "timestamp": datetime.utcnow()
    }
