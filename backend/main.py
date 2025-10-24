import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uuid

from core_logic import ingest_document, query_rag_pipeline, cleanup_temp_files

load_dotenv()  # Load environment variables

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting RAG Comparator API")
    yield
    cleanup_temp_files()
    logger.info("🛑 Shutting down RAG Comparator API")

app = FastAPI(
    title="RAG Comparator API",
    version="2.0.0",
    description="Advanced document comparison with RAG & NLP",
    lifespan=lifespan
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

    @validator('question')
    def validate_question(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Question must be at least 5 characters')
        if len(v) > 2000:
            raise ValueError('Question too long (max 2000 chars)')
        return v.strip()

@app.get("/")
def read_root():
    return {"status": "healthy", "version": "2.0.0", "service": "RAG Comparator"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_doc(doc_id: str = Form(...), file: UploadFile = File(...)):
    if doc_id not in ["doc_A", "doc_B"]:
        raise HTTPException(400, "doc_id must be 'doc_A' or 'doc_B'")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")

    content = await file.read()
    if len(content) > 40 * 1024 * 1024:  # Changed from 15MB to 40MB
        raise HTTPException(400, "File too large (max 40MB)")

    temp_file_path = None
    try:
        temp_file_path = f"./temp_{uuid.uuid4().hex}_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(content)

        chunks_added = ingest_document(temp_file_path, doc_id)

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        logger.info(f"✅ Uploaded {file.filename} as {doc_id}: {chunks_added} chunks")

        return JSONResponse({
            "status": "success",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_added": chunks_added
        })

    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.post("/query")
async def query_docs(request: QueryRequest):
    try:
        logger.info(f"🔍 Query: {request.question[:100]}...")
        answer = query_rag_pipeline(request.question)
        logger.info(f"✅ Query answered successfully")
        return JSONResponse({"answer": answer})

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"❌ Query error: {str(e)}")
        raise HTTPException(500, f"Query failed: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"🚨 Unhandled error: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
