# 🚀 Copilot Document Agent – Intelligent Document Processing AI

## 📋 Project Overview

An advanced AI-powered document processing system that leverages Retrieval-Augmented Generation (RAG) and contextual agents to understand, retrieve, and reason over professional documents.

## 🔧 Prerequisites

- Python 3.10+
- Node.js 18+
- pip
- npm

## 💻 System Architecture

```
Project Structure:
├── backend/       # Python RAG & Agent Backend
│   ├── src/
│   │   ├── agents/
│   │   ├── ingestion/
│   │   ├── retrieval/
│   │   └── ...
├── frontend/      # React TypeScript Interface
│   └── src/
│       ├── pages/
│       ├── components/
│       └── ...
```

### Key Components
- **Document Ingestion**: Parse PDFs, DOCX files
- **Vector Embedding**: Generate semantic embeddings
- **Retrieval Engine**: Cosine similarity search
- **LLM Integration**: Contextual question-answering
- **Agent Reasoning**: Multi-hop tool usage

## 🚀 Quick Start

### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 🐳 Docker Deployment

For an easier setup, the project includes Docker support. Simply run `docker-compose up --build` in the project root to build and start both backend and frontend services. Ensure you have Docker and Docker Compose installed, and configure your `.env` file with the necessary API keys before deployment.

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

## 🛠 Technologies

### Backend
- Python
- FastAPI
- LlamaIndex
- OpenAI
- FAISS
- SQLAlchemy

### Frontend
- React
- TypeScript
- Vite
