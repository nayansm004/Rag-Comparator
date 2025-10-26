import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from core_logic import ingest_document, query_rag_pipeline
import uuid

app = FastAPI(title="RAG Comparator API")

# CORS - allow all origins for Hugging Face
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "RAG Comparator API"}

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
    if len(content) > 40 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 40MB)")
    
    temp_file_path = f"./temp_{uuid.uuid4().hex}_{file.filename}"
    try:
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        chunks_added = ingest_document(temp_file_path, doc_id)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return JSONResponse({
            "status": "success",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_added": chunks_added
        })
    except Exception as e:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.post("/query")
async def query_docs(request: QueryRequest):
    try:
        answer = query_rag_pipeline(request.question)
        return JSONResponse({"answer": answer})
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)