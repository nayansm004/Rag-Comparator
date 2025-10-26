# RAG Document Comparator

<div align="center">

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.3-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

### AI-Powered Document Comparison Using RAG Architecture

*Compare two PDF documents side-by-side with intelligent insights powered by Google Gemini 2.5 Flash*

**[Try Live Demo](https://rag-comparator.netlify.app)** • [Backend API](https://nayansmgy-rag-comparator-api.hf.space)

</div>

---

## Overview

Upload two PDF documents and ask comparative questions to get AI-powered insights. Built with Retrieval-Augmented Generation (RAG) for accurate, context-aware document analysis.

### Key Features

- **Dual Document Analysis** - Compare two PDFs simultaneously with contextual understanding
- **Smart Query Expansion** - Automatically generates specialized queries for each document
- **Semantic Search** - FAISS vector database with HuggingFace embeddings for fast retrieval
- **Beautiful UI** - Modern React interface with Aurora background effects
- **100% Free Hosting** - Deployed on Hugging Face Spaces + Netlify

---

## Tech Stack

### Frontend
- **React 18.3** with Vite
- **Framer Motion** for animations
- **Tailwind CSS** for styling
- **Axios** for API calls

### Backend
- **FastAPI** - High-performance Python API
- **LangChain** - RAG orchestration
- **Google Gemini 2.5 Flash** - Language model for generation
- **FAISS** - Vector database for similarity search
- **HuggingFace Embeddings** - sentence-transformers/all-MiniLM-L6-v2
- **PyPDF** - PDF text extraction

### Infrastructure
- **Hugging Face Spaces** - Backend hosting (Docker)
- **Netlify** - Frontend hosting with CDN

---

## Architecture

```
User uploads PDFs → FastAPI processes → PyPDF extracts text
                                              ↓
                              Chunked with RecursiveCharacterTextSplitter
                                              ↓
                              Embedded with HuggingFace (all-MiniLM-L6-v2)
                                              ↓
                              Stored in FAISS vector database
                                              ↓
User asks question → Query expansion (Gemini) → Retrieve relevant chunks
                                              ↓
                              Gemini 2.5 Flash generates comparison answer
```

### RAG Pipeline Features

- **Smart Chunking**: 1200 tokens with 300 token overlap for context retention
- **Query Expansion**: Generates specialized queries for each document
- **Filtered Retrieval**: Separate retrievers for doc_A and doc_B (4 chunks each)
- **Synthesis**: Combines context from both documents for comprehensive answers

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google AI API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Local Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Run server
python main.py
```

Backend runs at `http://localhost:8000`

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## API Endpoints

### Upload Document
```http
POST /upload
Content-Type: multipart/form-data

Parameters:
- doc_id: "doc_A" or "doc_B"
- file: PDF file (max 40MB)
```

### Query Documents
```http
POST /query
Content-Type: application/json

Body:
{
  "question": "What are the key differences?"
}
```

### Health Check
```http
GET /health
```

---

## Deployment

### Backend (Hugging Face Spaces)

1. Create Space with Docker SDK at [huggingface.co/new-space](https://huggingface.co/new-space)
2. Push `huggingface/` directory contents
3. Add `GOOGLE_API_KEY` secret in Space settings

### Frontend (Netlify)

1. Connect GitHub repo to Netlify
2. Build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
3. Add environment variable:
   - `VITE_API_URL` = `https://nayansmgy-rag-comparator-api.hf.space`

---

## Environment Variables

**Backend** (`.env`)
```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

**Frontend** (`.env.development`)
```env
VITE_API_URL=http://localhost:8000
```

**Frontend** (`.env.production`)
```env
VITE_API_URL=https://nayansmgy-rag-comparator-api.hf.space
```

---

## Project Structure

```
rag-comparator/
├── backend/
│   ├── core_logic.py          # RAG pipeline implementation
│   ├── main.py                # FastAPI application
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── MainApp.jsx
│   │   │   └── AuroraBackground.jsx
│   │   └── App.jsx
│   └── package.json
│
└── huggingface/              # Deployment config
    ├── app.py
    ├── core_logic.py
    ├── Dockerfile
    └── requirements.txt
```

---

## Usage Examples

**Contract Comparison**
```
Q: "What are the main differences in termination clauses?"
A: Document A allows 30-day notice, while Document B requires 60-day notice...
```

**Research Analysis**
```
Q: "Compare the methodologies used in both studies."
A: Document A uses quantitative analysis, Document B employs qualitative methods...
```

**Policy Review**
```
Q: "Which document has more comprehensive privacy protections?"
A: Document B provides more detailed GDPR compliance measures...
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with Google Gemini • LangChain • FAISS • React

**[Try it now →](https://rag-comparator.netlify.app)**

</div>
