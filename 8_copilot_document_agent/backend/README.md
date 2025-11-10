# 🚀 Backend Architecture: Intelligent Document Processing System

## 📋 Overview

This backend implements a sophisticated Retrieval-Augmented Generation (RAG) system with multi-hop reasoning capabilities for intelligent document processing.

## 🏗️ Project Structure

```
backend/
├── .env
├── .env.example
├── main.py
├── pytest.ini
├── README.md
├── requirements.txt
│
├── data/
│   ├── app.db
│   ├── faiss_index.bin
│   └── faiss_index.bin.meta.json
│
└── src/
    ├── __init__.py
    │
    ├── agents/
    │   ├── __init__.py
    │   ├── agent_manager.py
    │   ├── rag_agent.py
    │   ├── tools.py
    │   └── prompts/
    │       ├── classify_prompt.py
    │       ├── final_prompt.py
    │       └── tool_execution_prompt.py
    │
    ├── core/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── logger.py
    │   └── models.py
    │
    ├── data/
    │   ├── __init__.py
    │   └── embedding.py
    │
    ├── db/
    │   ├── __init__.py
    │   ├── database.py
    │   ├── models.py
    │   ├── migrations/
    │   │   └── README.md
    │   └── repositories/
    │       ├── __init__.py
    │       ├── chunk_repository.py
    │       ├── document_repository.py
    │       ├── embedding_repository.py
    │       ├── query_repository.py
    │       └── response_repository.py
    │
    ├── ingestion/
    │   ├── __init__.py
    │   ├── chunker.py
    │   ├── docx_parser.py
    │   ├── embedding_generator.py
    │   ├── ingestion_pipeline.py
    │   ├── parser_base.py
    │   ├── pdf_parser.py
    │   └── text_cleaner.py
    │
    ├── interfaces/
    │   ├── __init__.py
    │   └── api_controller.py
    │
    ├── retrieval/
    │   ├── __init__.py
    │   ├── faiss_vector_store.py
    │   └── retriever.py
    │
    └── tests/
        ├── __init__.py
        ├── agents/
        │   └── test_rag_agent.py
        ├── errors/
        │   └── test_errors_and_edge_cases.py
        ├── fixtures/
        │   ├── __init__.py
        │   ├── contract.pdf
        │   ├── test_document.docx
        │   └── test_document.pdf
        ├── ingestion/
        │   ├── __init__.py
        │   ├── test_chunker.py
        │   ├── test_document_parser.py
        │   ├── test_docx_parser.py
        │   ├── test_embedding_generator.py
        │   ├── test_ingestion_pipeline.py
        │   ├── test_pdf_parser_ocr.py
        │   ├── test_pdf_parser.py
        │   ├── test_rag_agent_quality.py
        │   └── test_text_cleaner.py
        ├── integration/
        │   ├── __init__.py
        │   └── test_full_pipeline.py
        └── retrieval/
            ├── __init__.py
            ├── test_faiss_retrieval.py
            └── test_retriever.py

└── tests/
    └── fixtures/
        ├── test_document.docx
        └── test_document.pdf
```

## 🔍 System Architecture

### Key Components
- **Ingestion Pipeline**: Document parsing and embedding
- **Vector Retrieval**: Semantic search engine
- **Contextual Agents**: Multi-hop reasoning
- **Persistent Storage**: Document and embedding management

## 🚀 Component Overview

### 1. Core Layer
Provides foundational classes and utilities for the entire system.

#### Key Classes
- `Document`: Represents uploaded documents
- `Chunk`: Represents document text segments
- `EmbeddingVector`: Manages semantic embeddings
- `Config`: Handles environment configurations
- `Logger`: Advanced logging with rich formatting

### 2. Ingestion Module
Responsible for document processing and preparation.

#### Key Responsibilities
- Parse various document formats (PDF, DOCX)
- Clean and normalize text
- Generate semantic chunks
- Create vector embeddings

### 3. Retrieval Engine
Implements semantic search and context retrieval.

#### Key Features
- FAISS-based vector store
- Cosine similarity search
- Contextual chunk retrieval

### 4. Intelligent Agents
Enables advanced reasoning and multi-step query processing.

#### Agent Capabilities
- Retrieve relevant document contexts
- Execute multi-hop reasoning
- Use specialized tools for complex queries

### 5. Interfaces
Provides API endpoints for document interaction.

#### Endpoints
- `/upload`: Document ingestion
- `/query`: Contextual question-answering
- `/agent`: Advanced reasoning queries
- `/feedback`: User response improvement

## 🛠️ Technologies

### Backend Stack
- Python 3.10+
- FastAPI
- LlamaIndex
- OpenAI
- FAISS
- SQLAlchemy
- Rich (logging)

## 🧪 Testing

### Test Coverage
- Unit tests for each component
- Integration tests for full pipeline
- Error handling and edge case tests

### Running Tests
```bash
python -m pytest
```
