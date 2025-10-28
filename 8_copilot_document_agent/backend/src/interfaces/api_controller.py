from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
import os
from src.ingestion.ingestion_pipeline import IngestionPipeline
from src.agents.rag_agent import RAGAgent
from src.retrieval.retriever import Retriever
from src.ingestion.embedding_generator import EmbeddingGenerator
from src.retrieval.faiss_vector_store import FaissVectorStore
from openai import OpenAI
from src.core.logger import log_info, log_success

app = FastAPI(title="Copiloto Jurídico - API")

# --- Inicialização ---
vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/faiss_index.bin")

vector_store = FaissVectorStore(path=vector_store_path)  # índice persistido
embedding_model = EmbeddingGenerator(model="text-embedding-3-small")  # seu generator real
retriever = Retriever(vector_store=vector_store, embedding_model=embedding_model)
llm_client = OpenAI()  # LLM real
rag_agent = RAGAgent(retriever=retriever, client=llm_client)
pipeline = IngestionPipeline()

# --- Pydantic Model ---
class QueryRequest(BaseModel):
    question: str

# Healthcheck básico
@app.get("/healthcheck")
async def healthcheck():
    log_info("Healthcheck chamado.")
    return {"status": "ok", "message": "API rodando com sucesso"}

@app.post("/upload")
async def upload(file: UploadFile):
    log_info(f"📤 Recebendo upload: {file.filename}")

    # Define caminho temporário para salvar arquivo
    tmp_file_path = f"/tmp/{file.filename}"

    try:
        # Salva temporariamente
        with open(tmp_file_path, "wb") as f:
            f.write(await file.read())
        log_info(f"📂 Arquivo salvo temporariamente em: {tmp_file_path}")

        # Processa documento pelo pipeline
        result = pipeline.process(tmp_file_path)

        log_success("✅ Documento processado com sucesso!")
        return {"message": "Documento processado com sucesso!", "data": result}

    except Exception as e:
        log_info(f"❌ Falha ao processar upload: {e}")
        # Retorna o erro real para o cliente
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Remove arquivo temporário se existir
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            log_info(f"🧹 Arquivo temporário removido: {tmp_file_path}")

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    question = request.question
    log_info(f"🔍 Query recebida: {question}")

    try:
        # Cria um novo FaissVectorStore apontando para o mesmo path
        # Isso garante que o índice carregue sempre o estado mais recente do disco
        vector_store_latest = FaissVectorStore(path=vector_store_path)
        retriever_latest = Retriever(
            vector_store=vector_store_latest,
            embedding_model=embedding_model
        )
        rag_agent_latest = RAGAgent(
            retriever=retriever_latest,
            client=llm_client
        )

        # Busca os top_k chunks
        results = retriever_latest.search(question, top_k=5)
        contexts = [r["text"] for r in results]

        # Gera resposta do LLM
        response_text = rag_agent_latest.ask(question, top_k=5)

        log_success("✅ Query processada com sucesso!")
        return {
            "question": question,
            "answer": response_text,
            "contexts_used": contexts
        }

    except Exception as e:
        log_info(f"❌ Falha ao processar query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
