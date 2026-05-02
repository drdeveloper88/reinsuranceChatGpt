from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="AllianzGPT API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # Warm-up / validate vector store access
    from app.services.vectorstore import VectorStoreService
    VectorStoreService()

@app.get("/")
async def root():
    return {"message": "AllianzGPT backend is live"}
