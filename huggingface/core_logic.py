import os
import json
import glob
import logging
import uuid
import shutil
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

logger = logging.getLogger(__name__)

# Constants
DB_PERSIST_DIRECTORY = "./db"
VECTORSTORE_FILENAME = "faiss_index"
COLLECTION_NAME = "doc_comparator"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("❌ GOOGLE_API_KEY not set in environment variables.")

# Initialize components
try:
    # Use free HuggingFace embeddings instead of Gemini
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )

    vectorstore_path = os.path.join(DB_PERSIST_DIRECTORY, VECTORSTORE_FILENAME)
    if not os.path.exists(DB_PERSIST_DIRECTORY):
        os.makedirs(DB_PERSIST_DIRECTORY)

    if os.path.exists(vectorstore_path):
        vectorstore = FAISS.load_local(
            vectorstore_path, 
            embeddings_model,
            allow_dangerous_deserialization=True
        )
        logger.info("✅ Loaded existing FAISS vector store")
    else:
        # Create an empty FAISS vector store with a dummy document
        dummy_doc = Document(page_content="Initialization document", metadata={"source": "init"})
        vectorstore = FAISS.from_documents([dummy_doc], embeddings_model)
        vectorstore.save_local(vectorstore_path)
        logger.info("✅ Created new FAISS vector store")

    logger.info("✅ Gemini & FAISS components initialized successfully")

except Exception as e:
    logger.error(f"❌ Failed to initialize components: {e}")
    raise

def ingest_document(file_path: str, doc_id: str) -> int:
    """Load, chunk, and embed document into FAISS vector store."""
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        if not documents:
            raise ValueError("PDF is empty or unreadable")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        for chunk in chunks:
            chunk.metadata["source"] = doc_id
            chunk.metadata["doc_id"] = doc_id

        vectorstore.add_documents(chunks)
        vectorstore.save_local(vectorstore_path)

        logger.info(f"📄 Ingested {len(chunks)} chunks from {doc_id}")
        return len(chunks)

    except Exception as e:
        logger.error(f"❌ Ingestion error: {e}")
        raise

def query_rag_pipeline(question: str) -> str:
    """RAG pipeline with query expansion and synthesis using FAISS."""
    try:
        expansion_prompt = f"""Generate 2 specialized search queries for comparing two documents.

User Question: {question}

Return ONLY a JSON array with 2 queries (no explanation):
["query for document A", "query for document B"]

Example format: ["vacation policy details", "leave policy structure"]"""

        expansion_response = llm.invoke(expansion_prompt).content.strip()

        try:
            cleaned = expansion_response.replace("```json", "").replace("```", "").strip()
            queries = json.loads(cleaned)
            query_A = queries[0]
            query_B = queries[1]
            logger.info(f"🔍 Expanded queries: A='{query_A}', B='{query_B}'")
        except:
            logger.warning("⚠️ Query expansion failed, using original question")
            query_A = question
            query_B = question

        retriever_A = vectorstore.as_retriever(search_kwargs={"filter": {"doc_id": "doc_A"}, "k": 4})
        retriever_B = vectorstore.as_retriever(search_kwargs={"filter": {"doc_id": "doc_B"}, "k": 4})

        docs_A = retriever_A.get_relevant_documents(query_A)
        docs_B = retriever_B.get_relevant_documents(query_B)

        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join([f"[Chunk {i+1}]\n{doc.page_content}" for i, doc in enumerate(docs)])

        context_A = format_docs(docs_A)
        context_B = format_docs(docs_B)

        synthesis_prompt = f"""You are an expert document analyst. Compare the following information from two documents and provide a detailed, structured answer.

USER QUESTION:
{question}

DOCUMENT A CONTEXT:
{context_A}

DOCUMENT B CONTEXT:
{context_B}

INSTRUCTIONS:
1. Directly answer the user's question
2. Compare similarities and differences
3. Highlight key insights from each document
4. Be specific and reference both documents
5. Use clear formatting with paragraphs
6. If information is missing from either document, state it clearly

Provide a comprehensive comparison answer:"""

        final_answer = llm.invoke(synthesis_prompt).content
        logger.info(f"✅ Generated answer ({len(final_answer)} chars)")
        return final_answer

    except Exception as e:
        logger.error(f"❌ RAG pipeline error: {e}")
        raise

def cleanup_temp_files():
    """Clean up temporary files on shutdown."""
    try:
        temp_files = glob.glob("./temp_*")
        for f in temp_files:
            os.remove(f)
        logger.info(f"🧹 Cleaned up {len(temp_files)} temp files")
    except Exception as e:
        logger.error(f"⚠️ Cleanup error: {e}")