from pydantic import BaseModel, Field, validator, EmailStr, constr, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ==================== Auth Schemas ====================
class TokenPayload(BaseModel):
    sub: str
    exp: Optional[int] = None
    iat: Optional[int] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class LoginRequest(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., description="Username")
    password: constr(min_length=8, max_length=128) = Field(..., description="Password")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

class UserRegister(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")
    password: constr(min_length=8, max_length=128) = Field(..., description="Password")
    full_name: constr(max_length=100) = Field(..., description="Full name")
    
    @validator('password')
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Insurance Document Schemas ====================
class InsuranceType(str, Enum):
    HEALTH = "health"
    PROPERTY = "property"
    AUTO = "auto"
    LIFE = "life"
    BUSINESS = "business"
    OTHER = "other"

class DocumentMetadata(BaseModel):
    source: Optional[str] = Field(None, description="Source of document")
    insurance_type: Optional[InsuranceType] = Field(None, description="Type of insurance")
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    policy_number: Optional[str] = None
    coverage_type: Optional[str] = None
    keywords: Optional[List[str]] = Field(default_factory=list)
    document_type: Optional[str] = Field(None, description="e.g., policy, claim, FAQ")
    version: str = "1.0"
    confidentiality_level: str = "public"  # public, internal, confidential

class IngestRequest(BaseModel):
    namespace: constr(min_length=1, max_length=100) = Field("insurance", description="Namespace")
    documents: List[constr(min_length=1, max_length=50000)] = Field(..., min_items=1, max_items=100, description="List of documents")
    metadata: Optional[List[DocumentMetadata]] = None
    insurance_type: Optional[InsuranceType] = None
    enable_validation: bool = True
    
    @model_validator(mode='after')
    def validate_documents(self):
        documents = self.documents
        if len(documents) > 100:
            raise ValueError('Maximum 100 documents per request')
        total_chars = sum(len(doc) for doc in documents)
        if total_chars > 5_000_000:
            raise ValueError('Total document size exceeds 5MB limit')
        return self

class IngestResponse(BaseModel):
    status: str
    documents_ingested: int
    failed_documents: int
    namespace: str
    document_ids: List[str]
    warnings: Optional[List[str]] = None
    processing_time_ms: float
    timestamp: datetime

# ==================== Query Schemas ====================
class QueryRequest(BaseModel):
    query: constr(min_length=1, max_length=2000) = Field(..., description="Query text")
    top_k: int = Field(5, ge=1, le=20, description="Number of results")
    namespace: Optional[str] = Field("insurance", description="Namespace to query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")
    include_metadata: bool = True
    stream: bool = False
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class SourceDocument(BaseModel):
    page_content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None
    document_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    source_documents: List[SourceDocument]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: float
    model_used: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class StreamingChunk(BaseModel):
    type: str = "text"  # text, source, done, error
    content: Optional[str] = None
    delta: Optional[str] = None
    sources: Optional[List[SourceDocument]] = None
    error: Optional[str] = None

# ==================== Document Management Schemas ====================
class DocumentCollection(BaseModel):
    collection_id: str
    name: str
    description: Optional[str] = None
    document_count: int
    created_at: datetime
    updated_at: datetime
    insurance_types: List[InsuranceType]
    
    class Config:
        from_attributes = True

class DeleteDocumentsRequest(BaseModel):
    collection_id: Optional[str] = None
    namespace: Optional[str] = None
    document_ids: Optional[List[str]] = None
    delete_all: bool = False
    
    @model_validator(mode='after')
    def validate_delete_params(self):
        if not any(
            [self.collection_id, self.namespace, self.document_ids, self.delete_all]
        ):
            raise ValueError('At least one deletion parameter must be provided')
        return self

# ==================== Health Check Schemas ====================
class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
    components: Dict[str, str] = Field(default_factory=dict)

# ==================== Error Response Schemas ====================
class ErrorDetail(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ValidationErrorResponse(BaseModel):
    status: str = "validation_error"
    errors: List[Dict[str, Any]]
    timestamp: datetime
