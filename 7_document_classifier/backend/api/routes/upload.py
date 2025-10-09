# backend/api/routes/upload.py
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status, Request
import os
import tempfile
from pathlib import Path
from services.logger import classification_logger, error_logger, app_logger
from services.file_parser import parse_file

# Não fazemos mais imports de dataset aqui; usamos singletons no app.state
# Agent / IA
from agent.document_agent import DocumentAgent  # opcional, se já implementado

router = APIRouter()

# Safer file extension extraction
def get_file_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else ""

@router.post("/upload")
async def upload_file(
    request: Request,
    name: str = Form(None),
    file: UploadFile = File(...)
):
    # Acessa singletons inicializados no startup (main.py)
    vector_store = request.app.state.vector_store
    embedder = request.app.state.embedder
    prompt_engine = request.app.state.prompt_engine
    document_agent = getattr(request.app.state, "document_agent", None)  # opcional

    file_extension = get_file_extension(file.filename)
    app_logger.info(f"File upload attempt: {file.filename}")

    # Validação inicial de extensão
    if file_extension not in [".pdf", ".docx"]:
        error_logger.warning(f"Unsupported file format: {file_extension}")
        return {
            "status": "error",
            "content": "Not supported format"
        }

    tmp_path = None
    try:
        # Salva temporário com suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Extrai texto (parse_file deve aceitar string path)
        clean_text = parse_file(tmp_path)

        if not isinstance(clean_text, str) or not clean_text.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Empty or unreadable file")

        # Gera embedding (pode levantar erros - log e rethrow como 500)
        try:
            query_embedding = embedder.generate_embeddings(clean_text)
        except Exception as e:
            error_logger.exception("Error generating embedding")
            raise HTTPException(status_code=500, detail="Error generating embedding")

        # Predição por vetor
        predicted_class, confidence, _results = vector_store.predict_class(query_embedding)
        if predicted_class is None or confidence is None:
            # fallback: se vector_store estiver vazio, considera 'unknown'
            predicted_class = "unknown"
            confidence = 0.0

        classification_logger.info(f"Classifying document: {predicted_class} (conf={confidence:.4f})")

        # Somente tenta extrair se a categoria for suportada pelo PromptEngine
        extracted_data = {}
        if predicted_class in prompt_engine.prompts:
            try:
                extracted_data = prompt_engine.extract(predicted_class, clean_text)
            except Exception as e:
                # Falha na extração: log e segue (não interrompe o upload)
                error_logger.exception(f"Prompt extraction failed for class {predicted_class}: {e}")
                extracted_data = {"error": "extraction_failed", "raw_error": str(e)}
        else:
            app_logger.info(f"No extractor for predicted class '{predicted_class}'; skipping extraction")

        # Persiste via agent se disponível
        storage_result = None
        if document_agent:
            try:
                storage_result = document_agent.save({
                    "title": file.filename,
                    "type": predicted_class,
                    "content": clean_text,
                    "embedding": query_embedding,
                    "classification": predicted_class,
                    "confidence": float(confidence),
                    "metadata": extracted_data
                })
            except Exception as e:
                error_logger.exception(f"Failed to persist document: {e}")
                storage_result = {"error": "persistence_failed", "detail": str(e)}

        # Resposta
        return {
            "status": "success",
            "predicted_class": predicted_class,
            "confidence": round(float(confidence), 4),
            "extracted_data": extracted_data,
            "storage_result": storage_result
        }

    except HTTPException:
        # Re-raise HTTPException (já tratado)
        raise
    except Exception as e:
        error_logger.exception(f"Error processing upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal processing error")
    finally:
        # Sempre tenta apagar o arquivo temporário, se existir
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception as e:
            error_logger.exception(f"Failed to remove temp file {tmp_path}: {e}")