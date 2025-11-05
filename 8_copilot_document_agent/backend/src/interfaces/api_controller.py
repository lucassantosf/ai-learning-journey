# src/interfaces/api_controller.py
import os
import uuid
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel

from src.ingestion.ingestion_pipeline import IngestionPipeline
from src.agents.rag_agent import RAGAgent
from src.retrieval.retriever import Retriever
from src.ingestion.embedding_generator import EmbeddingGenerator
from src.retrieval.faiss_vector_store import FaissVectorStore
from openai import OpenAI
from src.core.logger import log_info, log_success, log_info as info

from src.agents.agent_manager import AgentManager

app = FastAPI(title="Copiloto Jurídico - API (optimized)")

# ---------------------------
# Inicialização (singletons)
# ---------------------------
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/faiss_index.bin")
DEFAULT_SYNC_TIMEOUT = int(os.getenv("API_SYNC_TIMEOUT_SECONDS", "60"))  # timeout para chamadas síncronas

vector_store = FaissVectorStore(path=VECTOR_STORE_PATH)  # índice persistido
embedding_model = EmbeddingGenerator(model="text-embedding-3-small")  # generator real
retriever = Retriever(vector_store=vector_store, embedding_model=embedding_model)

# client LLM (criado uma vez)
llm_client = OpenAI()  # manter uma única instância aqui para reaproveitar conexões

# Agentes / pipeline
rag_agent = RAGAgent(retriever=retriever, client=llm_client)
pipeline = IngestionPipeline()

# NOTE: AgentManager currently constructs its own OpenAI client.
# We'll keep constructing it for now, but later we will pass llm_client into AgentManager
# in the next step to avoid re-creating clients inside tools.
agent_manager = AgentManager(retriever=retriever)

# ---------------------------
# Simple in-memory job store
# For production replace with Redis / DB persistence
# ---------------------------
JOB_STORE: Dict[str, Dict[str, Any]] = {}
# JOB_STORE[job_id] = {"status": "pending"|"running"|"done"|"error", "result": ..., "error": ...}


# ---------------------------
# Pydantic models
# ---------------------------
class QueryRequest(BaseModel):
    question: str


# ---------------------------
# Healthcheck
# ---------------------------
@app.get("/healthcheck")
async def healthcheck():
    log_info("Healthcheck chamado.")
    return {"status": "ok", "message": "API rodando com sucesso"}


# ---------------------------
# Upload endpoint (unchanged)
# ---------------------------
@app.post("/upload")
async def upload(file: UploadFile):
    log_info(f"📤 Recebendo upload: {file.filename}")
    tmp_file_path = f"/tmp/{file.filename}"

    try:
        with open(tmp_file_path, "wb") as f:
            f.write(await file.read())
        log_info(f"📂 Arquivo salvo temporariamente em: {tmp_file_path}")

        result = pipeline.process(tmp_file_path)
        log_success("✅ Documento processado com sucesso!")
        return {"message": "Documento processado com sucesso!", "data": result}

    except Exception as e:
        log_info(f"❌ Falha ao processar upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            log_info(f"🧹 Arquivo temporário removido: {tmp_file_path}")


# ---------------------------
# /query - classic RAG (sync) with small optimizations
# ---------------------------
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Endpoint RAG clássico (não agent) — otimizado para usar top_k reduzido.
    Mantive seu fluxo original, mas com top_k menor (2).
    """
    question = request.question
    log_info(f"🔍 Query recebida: {question}")

    try:
        # Re-create vector_store to ensure latest state on disk (as you did before)
        vector_store_latest = FaissVectorStore(path=VECTOR_STORE_PATH)
        retriever_latest = Retriever(
            vector_store=vector_store_latest,
            embedding_model=embedding_model
        )
        rag_agent_latest = RAGAgent(
            retriever=retriever_latest,
            client=llm_client
        )

        # Busca os top_k chunks (reduzido para performance)
        results = retriever_latest.search(question, top_k=2)
        contexts = [r["text"] for r in results]

        # Gera resposta do LLM (pode demorar; este endpoint é síncrono)
        # Keep the same behavior but you can tune top_k on rag_agent.ask if param exists
        response_text = rag_agent_latest.ask(question, top_k=2)

        log_success("✅ Query processada com sucesso!")
        return {
            "question": question,
            "answer": response_text,
            "contexts_used": contexts
        }

    except Exception as e:
        log_info(f"❌ Falha ao processar query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Helper to run blocking agent call in thread with timeout
# ---------------------------
async def run_agent_with_timeout(question: str, timeout_seconds: int) -> str:
    """
    Runs agent_manager.ask in a thread and applies an asyncio timeout.
    Returns the result string, or raises asyncio.TimeoutError.
    """
    # run in a separate thread to not block event loop
    agent_coro = asyncio.to_thread(agent_manager.ask, question)
    return await asyncio.wait_for(agent_coro, timeout=timeout_seconds)


# ---------------------------
# /agent_query - synchronous but with configurable timeout (returns 504 on timeout)
# ---------------------------
@app.post("/agent_query")
async def agent_query(request: QueryRequest, timeout: Optional[int] = Query(None, description="Timeout seconds for sync call")):
    """
    Synchronous agent query endpoint. For short/fast queries use this.
    If processing exceeds `timeout` (or DEFAULT_SYNC_TIMEOUT), returns 504 and a friendly message.
    """
    question = request.question
    timeout_seconds = timeout or DEFAULT_SYNC_TIMEOUT

    log_info(f"🧠 Agent query recebida (sync, timeout={timeout_seconds}s): {question}")

    try:
        try:
            response_text = await run_agent_with_timeout(question, timeout_seconds)
        except asyncio.TimeoutError:
            log_info("⚠️ Agent query timeout (sync). Suggest using /agent_query_async for long-running tasks.")
            raise HTTPException(status_code=504, detail="Query processing timeout. Try /agent_query_async for long-running requests.")

        log_success("✅ Agent query processada com sucesso!")
        return {"question": question, "answer": response_text}

    except HTTPException:
        raise
    except Exception as e:
        log_info(f"❌ Falha ao processar agent_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Background worker for async jobs
# ---------------------------
def _background_worker(job_id: str, question: str):
    """
    This runs in the background (thread) and updates JOB_STORE with results.
    For production, replace with Celery/RQ and persistent storage (Redis, DB).
    """
    try:
        log_info(f"🔁 [BG] Job {job_id} started for question: {question}")
        JOB_STORE[job_id]["status"] = "running"
        result = agent_manager.ask(question)  # blocking call
        JOB_STORE[job_id]["status"] = "done"
        JOB_STORE[job_id]["result"] = result
        log_success(f"✅ [BG] Job {job_id} finished successfully.")
    except Exception as e:
        JOB_STORE[job_id]["status"] = "error"
        JOB_STORE[job_id]["error"] = str(e)
        log_info(f"❌ [BG] Job {job_id} failed: {e}")


# ---------------------------
# /agent_query_async - enqueue job and return job_id immediately
# ---------------------------
@app.post("/agent_query_async")
async def agent_query_async(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Enqueue the agent query to run in background and return a job_id.
    Client can poll /agent_query_result/{job_id} to get result.
    """
    question = request.question
    job_id = str(uuid.uuid4())
    JOB_STORE[job_id] = {"status": "pending", "result": None, "error": None, "question": question}

    # schedule background worker
    background_tasks.add_task(_background_worker, job_id, question)

    log_info(f"🧠 Agent query async enfileirada: job_id={job_id} question={question}")
    return {"job_id": job_id, "status": "pending"}


# ---------------------------
# Polling endpoint to get job result
# ---------------------------
@app.get("/agent_query_result/{job_id}")
async def agent_query_result(job_id: str):
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "question": job.get("question"),
        "result": job.get("result"),
        "error": job.get("error")
    }

@app.post("/agent")
async def agent_endpoint(request: QueryRequest):
    """
    Executa o agente com raciocínio multi-hop (multi-step) e ferramentas contextuais.
    """
    question = request.question
    log_info(f"🤖 /agent (multi-hop) chamado com pergunta: {question}")

    try:
        vector_store_latest = FaissVectorStore(path=VECTOR_STORE_PATH)
        retriever_latest = Retriever(
            vector_store=vector_store_latest,
            embedding_model=embedding_model
        )

        # Passamos o mesmo cliente LLM reutilizado
        advanced_agent = AgentManager(retriever=retriever_latest, client=llm_client)
        result = advanced_agent.ask(question)

        log_success("✅ /agent (multi-hop) processado com sucesso!")
        return result

    except Exception as e:
        log_info(f"❌ Erro ao executar /agent (multi-hop): {e}")
        raise HTTPException(status_code=500, detail=str(e))