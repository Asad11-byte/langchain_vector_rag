# Vector RAG App - Hybrid Search Document Retrieval System

A production-ready **Retrieval Augmented Generation (RAG)** application built with **FastAPI**, featuring **hybrid search** combining dense embeddings (Jina) and sparse embeddings (BM25/SPLADE) for optimal document retrieval.

---

## 🪧Vercel live dome 
- **Tap here ->** https://langchain-vector-rag.vercel.app

## 📋 Project Overview

This is a full-stack RAG system that allows users to:
- **Upload documents** (PDF, DOCX) to a vector database
- **Query documents** using natural language with hybrid semantic + keyword search
- **Retrieve relevant chunks** with reranking capabilities
- **Manage documents** (view, delete, track usage)
- **Evaluate retrieval quality** with built-in evaluation tools

Perfect for building **chatbots**, **knowledge bases**, **Q&A systems**, and **document search engines**.

---

## 🎯 Scope

### **In Scope (What This App Does)**
✅ **Document Management**
- Upload PDF and DOCX files
- Automatic chunking with configurable overlap
- Store document metadata (filename, source, chunk position)
- Delete documents and their associated embeddings

✅ **Hybrid Search**
- Dense embeddings via Jina API (`jina-embeddings-v3`)
- Sparse embeddings via fastembed (BM25/SPLADE)
- Combined scoring for better relevance

✅ **Vector Database**
- Qdrant Cloud integration
- Multi-vector support (dense + sparse)
- Efficient filtering by document_id
- Payload storage for metadata

✅ **Retrieval Pipeline**
- Top-K retrieval with configurable parameters
- Optional reranking with Cohere API
- Structured JSON responses

✅ **Cloud Deployment**
- Vercel serverless deployment
- Environment-based configuration
- Supabase storage for uploaded files

✅ **Evaluation Tools**
- Precision, recall, NDCG metrics
- Ground truth evaluation framework

---

## ⚠️ Limitations

### **Current Limitations**

❌ **Language Support**
- Primary: English (LangChain chunking optimized for English)
- Other languages work but with reduced chunking quality

❌ **File Format Support**
- Supported: PDF, DOCX
- **Not supported**: Images, audio, video, web URLs, JSON, CSV
- Binary files (images in PDFs) are not extracted

❌ **Chunk Size**
- Fixed chunking strategy (512 tokens by default)
- No adaptive chunking based on document structure
- No table/diagram-aware chunking

❌ **Real-time Updates**
- Documents are embedded synchronously (may timeout on large files)
- No bulk import for multiple documents
- No incremental updates to chunks

❌ **Scalability**
- Vercel timeout limit: **60 seconds** (file upload may fail for >10MB files)
- Memory limit: **3GB** per serverless function
- Not suitable for extremely large documents (>50MB)

❌ **API Rate Limits**
- Subject to Jina API rate limits
- Subject to Qdrant Cloud rate limits
- Subject to Cohere reranker rate limits

❌ **Security**
- CORS is open (`allow_origins=["*"]`) - tighten for production
- No user authentication/authorization built-in
- No request rate limiting
- No API key management

❌ **Features NOT Included**
- Streaming responses
- Chat history/conversation memory
- Custom prompt templates
- Fine-tuning of embeddings
- Multi-language support
- Query expansion/reformulation
- Semantic caching
- Cost tracking/usage analytics

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (index.html)   │
└────────┬────────┘
         │ HTTP
         ▼
┌──────────────────────────┐
│   FastAPI Server         │
│  (api/index.py)          │
└────┬──────┬──────┬───────┘
     │      │      │
     ▼      ▼      ▼
  Upload  Query  Docs API
     │      │      │
     └──────┬──────┘
            ▼
    ┌──────────────────┐
    │  Core Modules    │
    ├──────────────────┤
    │ • vectorstore.py │ (Qdrant ops)
    │ • embeddings.py  │ (Jina API)
    │ • sparse.py      │ (fastembed)
    │ • ingestion.py   │ (chunking)
    └────┬─────────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
 Qdrant    Jina API   Supabase   Cohere
 (Vector   (Dense    (Storage)   (Rerank)
  DB)      Embed)
```

---

## 🚀 Quick Start

### **Prerequisites**
- **Python 3.11+** (required)
- Qdrant Cloud account
- Jina API key
- Supabase account (optional, for file storage)
- Cohere API key (optional, for reranking)

### **1. Clone & Setup**
```bash
git clone <your-repo>
cd rag-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Configure Environment**
Create `.env` file:
```bash
# Qdrant
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION_NAME=rag_documents

# Jina Embeddings
JINA_API_KEY=jina_xxx

# Supabase (for file storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
SUPABASE_STORAGE_BUCKET=documents

# Optional - Reranking
COHERE_API_KEY=your_cohere_key

# Optional - Generation
GROQ_API_KEY=your_groq_key

# App Settings
ENVIRONMENT=development
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=10
TOP_K_RERANK=4
```

### **3. Run Locally**
```bash
uvicorn app.main:app --reload
```
Visit: http://localhost:8000

---

## 📦 Requirements

### **Core Dependencies**
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115.0 | Web framework |
| uvicorn | 0.30.6 | ASGI server |
| langchain | 0.3.1 | LLM orchestration |
| langchain-community | 0.3.1 | Community integrations |
| qdrant-client | 1.11.2 | Vector DB client |
| fastembed | 0.3.6 | Sparse embeddings (BM25/SPLADE) |
| jina-embeddings-v3 | via langchain | Dense embeddings via Jina API |
| supabase | 2.7.4 | File storage |
| pydantic | 2.9.2 | Data validation |
| python-dotenv | 1.0.1 | Environment management |

### **Python Version**
**Required: Python 3.11+**

Check your version:
```bash
python --version
```

---

## 🔌 API Endpoints

### **Upload Document**
```http
POST /api/upload
Content-Type: multipart/form-data

{
  "file": <binary_file>,
  "document_name": "my_document"
}

Response (200 OK):
{
  "document_id": "uuid",
  "chunks_count": 42,
  "file_size": 1024000,
  "status": "success"
}
```

### **Query Documents**
```http
POST /api/query
Content-Type: application/json

{
  "query": "What is machine learning?",
  "top_k": 10,
  "use_rerank": true
}

Response (200 OK):
{
  "results": [
    {
      "score": 0.95,
      "text": "Machine learning is...",
      "source_filename": "ml_guide.pdf",
      "page": 5
    }
  ],
  "query_time_ms": 234
}
```

### **List Documents**
```http
GET /api/documents

Response (200 OK):
{
  "documents": [
    {
      "document_id": "uuid",
      "filename": "research.pdf",
      "chunks_count": 50,
      "uploaded_at": "2024-07-24T10:30:00Z"
    }
  ]
}
```

### **Delete Document**
```http
DELETE /api/documents/{document_id}

Response (204 No Content)
```

### **Health Check**
```http
GET /health

Response (200 OK):
{
  "status": "ok"
}
```

---

## 🚢 Deployment to Vercel

### **1. Push to GitHub**
```bash
git add -A
git commit -m "Ready for Vercel deployment"
git push origin main
```

### **2. Connect to Vercel**
- Go to [vercel.com](https://vercel.com)
- New Project → Import Git Repository
- Select your GitHub repo

### **3. Configure Environment Variables**
In Vercel Dashboard → Settings → Environment Variables:
```
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=xxx
QDRANT_COLLECTION_NAME=rag_documents
JINA_API_KEY=jina_xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
COHERE_API_KEY=xxx (optional)
GROQ_API_KEY=xxx (optional)
ENVIRONMENT=production
```

### **4. Deploy**
Click "Deploy" and wait 2-3 minutes.

Your app will be live at: `https://your-project.vercel.app`

### **Vercel Limitations**
- Timeout: 60 seconds per request
- Memory: 3GB per function
- Max file size: ~50MB
- Cold starts: ~3-5 seconds

---

## 🐛 Troubleshooting

### **Problem: `ModuleNotFoundError: No module named 'fastembed'`**
**Solution:** Uncomment `fastembed==0.3.6` in `requirements.txt`

### **Problem: `JINA_API_KEY not set`**
**Solution:** Ensure `JINA_API_KEY` is in Vercel Environment Variables (not `.env`)

### **Problem: Qdrant connection timeout**
**Solution:** 
- Check Qdrant URL is correct
- Verify API key has access
- Check firewall/IP allowlist on Qdrant Cloud

### **Problem: Static files not found (404 on root)**
**Solution:** Ensure `app/static/index.html` exists in your deployment

### **Problem: Request timeout on large files**
**Solution:** Vercel has 60s timeout. For files >20MB, consider:
- Breaking into smaller chunks before upload
- Using background jobs (Firebase, AWS Lambda)
- Running self-hosted

---

## 📈 Performance Tips

### **Optimize Retrieval Speed**
```python
# In config.py, tune these:
TOP_K_RETRIEVAL = 5    # Reduce from 10 (fewer API calls)
TOP_K_RERANK = 2       # Reduce reranking if slow
CHUNK_SIZE = 256       # Smaller chunks = faster search
```

### **Reduce Embedding Costs**
- Batch upload documents in low-traffic hours
- Reuse embeddings when possible
- Monitor Jina API usage

### **Improve Retrieval Quality**
- Increase `CHUNK_SIZE` for longer context
- Use reranking for top results
- Tune `CHUNK_OVERLAP` based on domain

---

## 📊 Evaluation

Run evaluation on a test set:
```bash
curl -X POST http://localhost:8000/api/eval \
  -H "Content-Type: application/json" \
  -d '{
    "ground_truth_file": "ground_truth.json",
    "top_k": 10
  }'
```

Expected metrics: NDCG, Precision@10, Recall@10

---

## 🔒 Security Checklist for Production

- [ ] Tighten CORS: Change `allow_origins=["*"]` to specific domains
- [ ] Add API key authentication to endpoints
- [ ] Enable rate limiting (use middleware)
- [ ] Validate file uploads (size, type, virus scan)
- [ ] Use HTTPS only
- [ ] Rotate API keys regularly
- [ ] Add request logging/monitoring
- [ ] Implement request signing for sensitive operations

---

## 📝 License

[Add your license here]

---

## 🤝 Contributing

[Add contribution guidelines if applicable]

---

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Jina API Docs](https://jina.ai/)
- [LangChain Docs](https://python.langchain.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/supported-languages#python)

---

## ⚡ Quick Reference

```bash
# Local development
uvicorn app.main:app --reload

# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Must be 3.11+

# Create .env from template
cp .env.example .env

# Run tests
pytest tests/

# Deploy to Vercel
git push origin main
```

---

**Last Updated:** July 24, 2026 | **Python:** 3.11+ | **Status:** Production-Ready