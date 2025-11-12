# src/interfaces/api_controller.py
import os
import uuid
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from src.ingestion.ingestion_pipeline import IngestionPipeline
from src.agents.rag_agent import RAGAgent
from src.retrieval.retriever import Retriever
from src.ingestion.embedding_generator import EmbeddingGenerator
from src.retrieval.faiss_vector_store import FaissVectorStore
from openai import OpenAI
from src.core.logger import log_info, log_success, log_error
from src.agents.agent_manager import AgentManager

from src.db.database import init_db, get_db
from src.db.models import Document, Chunk, Embedding, Query as QueryModel, Response as ResponseModel
from sqlalchemy.orm import Session

# ======================================================
# 🚀 Inicialização
# ======================================================
app = FastAPI(title="Copiloto Jurídico - API (optimized)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    init_db()

VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/faiss_index.bin")
DEFAULT_SYNC_TIMEOUT = int(os.getenv("API_SYNC_TIMEOUT_SECONDS", "60"))

vector_store = FaissVectorStore(path=VECTOR_STORE_PATH)
embedding_model = EmbeddingGenerator(model="text-embedding-3-small")
retriever = Retriever(vector_store=vector_store, embedding_model=embedding_model)
llm_client = OpenAI()
rag_agent = RAGAgent(retriever=retriever, client=llm_client)
pipeline = IngestionPipeline()
agent_manager = AgentManager(retriever=retriever)

JOB_STORE: Dict[str, Dict[str, Any]] = {}

# ======================================================
# 🧠 Schemas
# ======================================================
class QueryRequest(BaseModel):
    question: str


# ======================================================
# 🩺 Healthcheck
# ======================================================
@app.get("/healthcheck")
async def healthcheck():
    log_info("Healthcheck chamado.")
    return {"status": "ok", "message": "API rodando com sucesso"}


# ======================================================
# 📤 Upload de documento
# ======================================================
@app.post("/upload")
async def upload(file: UploadFile):
    # Validate file basics
    if not file.filename:
        log_error("❌ Nome do arquivo inválido")
        raise HTTPException(status_code=400, detail="Nome do arquivo inválido")

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    ALLOWED_EXTENSIONS = {'.pdf', '.docx'}
    if file_ext not in ALLOWED_EXTENSIONS:
        log_error(f"❌ Tipo de arquivo não suportado: {file_ext}")
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF e DOCX são suportados")

    # Generate unique temporary filename
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    tmp_file_path = f"/tmp/{unique_filename}"

    try:
        # Stream file to disk
        file_size = 0
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
        
        with open(tmp_file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                f.write(chunk)
                file_size += len(chunk)
                
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="Arquivo muito grande. Limite máximo: 50MB")

        log_info(f"📂 Arquivo salvo temporariamente em: {tmp_file_path}")

        # Process the file
        result = pipeline.process(tmp_file_path)
        log_success("✅ Documento processado com sucesso!")
        
        return {
            "message": "Documento processado com sucesso!", 
            "data": result,
            "filename": file.filename,
            "size": file_size
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        log_error(f"❌ Falha ao processar upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    finally:
        # Always attempt to remove temporary file
        if os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
                log_info(f"🧹 Arquivo temporário removido: {tmp_file_path}")
            except Exception as cleanup_error:
                log_error(f"Erro ao remover arquivo temporário: {cleanup_error}")


# ======================================================
# 🔍 /query — consulta clássica RAG
# ======================================================
@app.post("/query")
async def query_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    question = request.question.strip()
    log_info(f"🔍 Query recebida: {question}")

    try:
        vector_store_latest = FaissVectorStore(path=VECTOR_STORE_PATH)
        retriever_latest = Retriever(vector_store=vector_store_latest, embedding_model=embedding_model)
        rag_agent_latest = RAGAgent(retriever=retriever_latest, client=llm_client)

        results = retriever_latest.search(question, top_k=2)
        contexts = [r["text"] for r in results]
        answer = rag_agent_latest.ask(question, top_k=2)

        # 💾 Persiste no banco
        query_db = QueryModel(question=question)
        db.add(query_db)
        db.commit()
        db.refresh(query_db)

        response_db = ResponseModel(query_id=query_db.id, answer=answer, data={"contexts": contexts})
        db.add(response_db)
        db.commit()

        log_success(f"✅ Query salva no banco: id={query_db.id}")
        return {"question": question, "answer": answer, "contexts_used": contexts}

    except Exception as e:
        db.rollback()
        log_error(f"❌ Falha ao processar /query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# 🤖 /agent_query — síncrono com timeout
# ======================================================
async def run_agent_with_timeout(question: str, timeout_seconds: int) -> str:
    return await asyncio.wait_for(asyncio.to_thread(agent_manager.ask, question), timeout=timeout_seconds)

@app.post("/agent_query")
async def agent_query(
    request: QueryRequest,
    timeout: Optional[int] = Query(None, description="Timeout seconds for sync call"),
    db: Session = Depends(get_db)
):
    question = request.question.strip()
    timeout_seconds = timeout or DEFAULT_SYNC_TIMEOUT
    log_info(f"🧠 Agent query recebida (sync, timeout={timeout_seconds}s): {question}")

    try:
        try:
            answer = await run_agent_with_timeout(question, timeout_seconds)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Tempo limite atingido. Tente /agent_query_async.")

        # 💾 Persiste no banco
        query_db = QueryModel(question=question)
        db.add(query_db)
        db.commit()
        db.refresh(query_db)

        # ✅ Armazena texto principal + reasoning em JSON
        response_db = ResponseModel(
            query_id=query_db.id,
            answer=answer["final_answer"],
            data={
                "reasoning": answer["reasoning"],
                "tools_used": answer["tools_used"]
            }
        )
        db.add(response_db)
        db.commit()

        log_success(f"✅ Agent query salva no banco: id={query_db.id}")
        return {"question": question, "answer": answer}

    except Exception as e:
        db.rollback()
        log_error(f"❌ Erro em /agent_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# 🧵 /agent_query_async — processamento em background
# ======================================================
def _background_worker(job_id: str, question: str, db: Session):
    try:
        JOB_STORE[job_id]["status"] = "running"
        result = agent_manager.ask(question)

        # 💾 Persiste no banco ao final
        query_db = QueryModel(question=question)
        db.add(query_db)
        db.commit()
        db.refresh(query_db)

        response_db = ResponseModel(query_id=query_db.id, answer=result)
        db.add(response_db)
        db.commit()

        JOB_STORE[job_id]["status"] = "done"
        JOB_STORE[job_id]["result"] = result
        log_success(f"✅ [BG] Job {job_id} concluído com sucesso.")
    except Exception as e:
        db.rollback()
        JOB_STORE[job_id]["status"] = "error"
        JOB_STORE[job_id]["error"] = str(e)
        log_error(f"❌ [BG] Job {job_id} falhou: {e}")

@app.post("/agent_query_async")
async def agent_query_async(request: QueryRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    question = request.question
    job_id = str(uuid.uuid4())
    JOB_STORE[job_id] = {"status": "pending", "result": None, "error": None, "question": question}

    background_tasks.add_task(_background_worker, job_id, question, db)
    log_info(f"🧠 Agent query async enfileirada: job_id={job_id}")
    return {"job_id": job_id, "status": "pending"}


@app.get("/agent_query_result/{job_id}")
async def agent_query_result(job_id: str):
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID não encontrado")
    return job


# ======================================================
# 🧩 /agent — modo multi-hop
# ======================================================
@app.post("/agent")
async def agent_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    question = request.question.strip()
    log_info(f"🤖 /agent (multi-hop) chamado com pergunta: {question}")

    try:
        vector_store_latest = FaissVectorStore(path=VECTOR_STORE_PATH)
        retriever_latest = Retriever(vector_store=vector_store_latest, embedding_model=embedding_model)
        advanced_agent = AgentManager(retriever=retriever_latest, client=llm_client)

        result = advanced_agent.ask(question)

        # 💾 Persiste no banco
        query_db = QueryModel(question=question)
        db.add(query_db)
        db.commit()
        db.refresh(query_db)

        response_db = ResponseModel(query_id=query_db.id, answer=json.dumps(result, ensure_ascii=False))

        db.add(response_db)
        db.commit()

        log_success(f"✅ /agent query salva no banco: id={query_db.id}")
        return {"question": question, "answer": result}

    except Exception as e:
        db.rollback()
        log_error(f"❌ Erro ao executar /agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# 🧪 /db — diagnóstico rápido
# ======================================================
@app.get("/db")
def debug_db(db: Session = Depends(get_db)):
    doc_count = db.query(Document).count()
    chunk_count = db.query(Chunk).count()
    emb_count = db.query(Embedding).count()
    docs = db.query(Document.id, Document.filename).all()
    return {
        "documents_total": doc_count,
        "chunks_total": chunk_count,
        "embeddings_total": emb_count,
        "documents": [{"id": d.id, "filename": d.filename} for d in docs],
    }

# ======================================================
# 📜 Query History Endpoints
# ======================================================
@app.get("/query-history")
def get_query_history(
    limit: int = Query(20, description="Number of recent queries to retrieve"),
    keyword: Optional[str] = Query(None, description="Optional keyword to filter queries")
):
    """
    Retrieve query history with optional filtering and pagination.
    
    - If no keyword is provided, returns the most recent queries
    - If a keyword is provided, searches for queries containing the keyword
    """
    from src.db.repositories.query_repository import QueryRepository
    from src.db.models import Response

    db = next(get_db())
    query_repo = QueryRepository(db)

    try:
        if keyword:
            queries = query_repo.search_by_keyword(keyword, limit)
        else:
            queries = query_repo.list_recent(limit)

        # Transform queries to a more frontend-friendly format
        history = []
        for query in queries:
            # Fetch the most recent response for this query
            response = (
                db.query(Response)
                .filter(Response.query_id == query.id)
                .order_by(Response.created_at.desc())
                .first()
            )

            history.append({
                "id": query.id,
                "question": query.question,
                "answer": response.answer if response else "Sem resposta",
                "created_at": query.created_at.isoformat(),
                "metadata": response.data if response else {}
            })

        return {
            "total": len(history),
            "queries": history
        }
    except Exception as e:
        log_error(f"❌ Falha ao recuperar histórico de consultas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/query-history")
def clear_query_history():
    """
    Clear entire query history.
    
    Requires careful consideration before use.
    """
    from src.db.repositories.query_repository import QueryRepository

    db = next(get_db())
    query_repo = QueryRepository(db)

    try:
        query_repo.clear_history()
        log_success("✅ Histórico de consultas limpo com sucesso")
        return {"message": "Histórico de consultas limpo com sucesso"}
    except Exception as e:
        log_error(f"❌ Falha ao limpar histórico de consultas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/query-history/{query_id}")
def delete_query_by_id(query_id: int):
    """
    Delete a specific query from history by its ID.
    """
    from src.db.repositories.query_repository import QueryRepository

    db = next(get_db())
    query_repo = QueryRepository(db)

    try:
        success = query_repo.delete_by_id(query_id)
        if success:
            log_success(f"✅ Consulta {query_id} removida do histórico")
            return {"message": f"Consulta {query_id} removida do histórico"}
        else:
            log_error(f"❌ Consulta {query_id} não encontrada")
            raise HTTPException(status_code=404, detail="Consulta não encontrada")
    except Exception as e:
        log_error(f"❌ Falha ao remover consulta do histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))
