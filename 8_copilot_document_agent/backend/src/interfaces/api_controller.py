from fastapi import FastAPI, UploadFile, HTTPException
import os
from src.ingestion.ingestion_pipeline import IngestionPipeline
from src.core.logger import log_info, log_success

app = FastAPI(title="Copiloto Jurídico - API")

pipeline = IngestionPipeline()

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
