from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.ingestion.ingestion_pipeline import IngestionPipeline
from src.core.logger import log_info

app = FastAPI(title="Copiloto Jurídico - API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = IngestionPipeline()

@app.get("/healthcheck")
async def healthcheck():
    """
    Verifica se a API está ativa.
    """
    log_info("Healthcheck chamado.")
    return {"status": "ok", "message": "API rodando com sucesso"}

@app.post("/upload")
async def upload(file: UploadFile):
    log_info(f"Recebendo upload: {file.filename}")
    file_path = f"/tmp/{file.filename}"

    # salva temporariamente o arquivo
    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = pipeline.process(file_path)
    return {"message": "Documento processado com sucesso!", "data": result}
