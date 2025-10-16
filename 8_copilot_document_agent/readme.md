# 🚀 Copilot Document Agent – 4 Week Roadmap

An intelligent AI copilot that understands, retrieves, and reasons over professional documents using RAG and contextual agents.

---

## ✅ To Do List

### 🧩 **Week 1 – Fundamentals & RAG Base**
**🎯 Goal:**  
Set up the core project structure, environment, and basic document ingestion/indexing pipeline.

#### Tasks
- [ ] **Create GitHub repository**
  - [ ] Name: `copilot-document-agent`
  - [ ] Add `.gitignore`, `README.md`, and folder structure:
    ```
    /src
      /ingestion
      /retrieval
      /agents
      /tools
      /interfaces
      /data
    ```
- [ ] **Set up Python environment**
  - [ ] Create virtual env (`venv`) and `requirements.txt`
  - [ ] Dependencies: `llama-index`, `openai`, `faiss-cpu`, `python-dotenv`, `pdfplumber`, `docx2txt`, `rich`
- [ ] **Document ingestion module**
  - [ ] Implement PDF parsing (`pdfplumber`)
  - [ ] Implement DOCX parsing (`docx2txt`)
  - [ ] Extract clean text and basic metadata (title, pages, etc.)
- [ ] **Local vector database**
  - [ ] Generate embeddings (`text-embedding-3-large`)
  - [ ] Store vectors in FAISS with metadata
- [ ] **Initial API with FastAPI**
  - [ ] Endpoint: `/upload`
  - [ ] Receive document → extract text → index in FAISS
  - [ ] Return success + document ID

✅ **Deliverable:**  
Functional pipeline that:
1. Receives and parses documents  
2. Generates embeddings and indexes them  
3. Provides a working upload API

---

### ⚙️ **Week 2 – Retrieval & Contextual QA**
**🎯 Goal:**  
Enable the system to retrieve and answer questions based on indexed documents.

#### Tasks
- [ ] **Retrieval module**
  - [ ] Implement cosine similarity search (top 3–5 chunks)
  - [ ] Return relevant context with metadata
- [ ] **Integrate LLM (GPT-4o-mini)**
  - [ ] Prompt template: *“Use the following context to answer the question.”*
  - [ ] Connect retrieval output to LLM query
- [ ] **Create `/query` endpoint**
  - [ ] Input: `{ "question": "..." }`
  - [ ] Output: contextual answer + snippets used
- [ ] **Improve chunking**
  - [ ] Add overlap (e.g. 500 tokens + 100 overlap)
- [ ] **Add logging**
  - [ ] Use `rich` for colored logs (response time, chunk count)
- [ ] **Write unit tests**
  - [ ] Test retrieval, chunking, and LLM integration

✅ **Deliverable:**  
System can:
1. Search document context  
2. Generate accurate, contextual answers  
3. Display retrieved snippets

---

### 🧠 **Week 3 – Agent & Multi-hop Reasoning**
**🎯 Goal:**  
Turn the RAG system into an intelligent agent capable of reasoning and using specialized tools.

#### Tasks
- [ ] **Create base agent**
  - [ ] Use `LlamaIndex Agent`
  - [ ] Add FAISS retriever as a tool
- [ ] **Add contextual tools**
  - [ ] `summarize_document(doc_id)`
  - [ ] `extract_legal_clauses(doc_id)`
  - [ ] `compare_documents(docA, docB)`
- [ ] **Implement multi-hop reasoning**
  - [ ] Agent combines results from multiple tools to form complex answers
  - [ ] Example: *“Compare the obligations in contracts A and B.”*
- [ ] **Create `/agent` endpoint**
  - [ ] Input: free-form question  
  - [ ] Output: reasoning steps + tools used + final answer
- [ ] **Enhance prompts**
  - [ ] Add few-shot examples showing citations and structured reasoning

✅ **Deliverable:**  
An agent that:
1. Uses tools dynamically  
2. Performs multi-hop reasoning  
3. Explains its answers with sources

---

### 💼 **Week 4 – Refinement, Feedback & Deploy**
**🎯 Goal:**  
Polish the MVP, add persistence and feedback, and make it deploy-ready.

#### Tasks
- [ ] **Add OCR support (optional)**
  - [ ] Use `pytesseract` for scanned PDFs
- [ ] **Database persistence**
  - [ ] Use SQLite or Postgres
  - [ ] Store documents, embeddings, queries, and responses
- [ ] **Feedback loop**
  - [ ] `/feedback` endpoint to store user corrections
  - [ ] Save improved examples for fine-tuning or evaluation
- [ ] **Simple interface**
  - [ ] Build Streamlit or Gradio app
  - [ ] Upload doc → ask question → view answer + citations
- [ ] **Docker packaging**
  - [ ] Create `Dockerfile` and `docker-compose.yml`
  - [ ] Include services: API, DB, (optional) UI
- [ ] **Documentation**
  - [ ] Update README with:
    - Project overview  
    - Local setup  
    - Folder structure  
    - API reference  
    - Future roadmap

✅ **Deliverable:**  
Fully functional MVP that:
1. Handles documents end-to-end  
2. Learns from feedback  
3. Runs locally or via Docker  
4. Includes full documentation

---

## 🏁 **Summary**
| Week | Theme | Key Outcome |
|------|--------|-------------|
| 1 | Fundamentals & RAG Base | Upload and index documents |
| 2 | Retrieval & QA | Contextual question-answering |
| 3 | Agent & Reasoning | Tool-driven intelligent agent |
| 4 | Refinement & Deploy | Full MVP with feedback and Docker |

---
