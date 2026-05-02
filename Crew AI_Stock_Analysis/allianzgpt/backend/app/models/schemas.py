from pydantic import BaseModel
from typing import List, Optional

class TokenPayload(BaseModel):
    sub: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

class IngestRequest(BaseModel):
    namespace: str = "default"
    documents: List[str]

class QueryRequest(BaseModel):
    query: str
    top_k: int = 4

class QueryResponse(BaseModel):
    answer: str
    source_documents: Optional[List[dict]]
