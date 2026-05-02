import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime

from app.api.routes import router, vector_service
from app.core.config import settings
from app.services.seeder import DataSeeder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting Insurance ChatBot API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Type: {settings.llm_type}")
    logger.info(f"Embedding Type: {settings.embedding_type}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    
    # Seed insurance samples into the same vector store the API uses (skips if already populated)
    try:
        DataSeeder.seed_insurance_data(vector_service)
        logger.info("Vector store seed check completed")
    except Exception as e:
        logger.error(f"Failed to seed vector store: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Insurance ChatBot API")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Insurance ChatBot API with RAG and LangChain",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware: Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.localhost",
        "*.insurance.com",
        "backend",
        "insurance-backend",
        "frontend",
        "insurance-frontend",
    ]
)

# Middleware: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include routers
app.include_router(router, prefix="/api")

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "validation_error",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{settings.app_name} is live",
        "version": "1.0.0",
        "docs_url": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
