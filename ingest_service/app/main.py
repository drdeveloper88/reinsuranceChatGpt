from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import httpx

class IngestEvent(BaseModel):
    namespace: str = "default"
    contents: list[str]

INGEST_API_URL = os.getenv("BACKEND_INGEST_URL", "http://localhost:8000/api/ingest")
INGEST_API_KEY = os.getenv("BACKEND_API_KEY", "")

app = FastAPI(title="AllianzGPT Ingest Service")

@app.post("/ingest")
async def ingest(event: IngestEvent):
    if not event.contents:
        raise HTTPException(status_code=400, detail="No content provided")

    payload = {"namespace": event.namespace, "documents": event.contents}

    headers = {"Content-Type": "application/json"}
    if INGEST_API_KEY:
        headers["Authorization"] = f"Bearer {INGEST_API_KEY}"

    async with httpx.AsyncClient() as client:
        r = await client.post(INGEST_API_URL, json=payload, headers=headers, timeout=90)

    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r.json()

@app.get("/health")
async def health():
    return {"status": "ok", "from": "ingest_service"}
