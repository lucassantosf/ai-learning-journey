from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status
import os, tempfile, json
from pathlib import Path
from services.docx_parser import DocxParser
from services.pdf_parser import PDFParser
from services.logger import classification_logger, error_logger, app_logger
from agent.embedder import Embedder
from agent.vector_store import VectorStore
from agent.prompt_engine import PromptEngine

router = APIRouter()

# Carrega dataset na inicialização
DATASET_FILE = Path(__file__).resolve().parent.parent.parent / "dataset" / "embeddings.json"
vector_store = VectorStore()
with open(DATASET_FILE, "r", encoding="utf-8") as f:
    dataset = json.load(f)
    for embedding, metadata in dataset:
        # Normaliza o formato
        if isinstance(embedding, list) and len(embedding) == 1 and isinstance(embedding[0], list):
            embedding = embedding[0]  # remove nesting [[...]] → [...]
        elif isinstance(embedding, float):
            embedding = [embedding]

        print("Embedding carregado:", type(embedding), len(embedding) if isinstance(embedding, list) else embedding)
        vector_store.add(embedding, metadata)

embedder = Embedder()

# Safer file extension extraction
def get_file_extension(filename):
    """
    Safely extract file extension, handling various filename formats
    """
    # Use os.path.splitext and ensure we get a lowercase extension
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else ""

@router.post("/upload")
async def upload_file(
    name: str = Form(None),
    file: UploadFile = File(...)
):
    try: 
        file_extension = get_file_extension(file.filename)

        # Log file upload attempt
        app_logger.info(f"File upload attempt: {file.filename}")

        # Check for supported file extensions first
        if file_extension.lower() not in [".pdf", ".docx"]:
            error_logger.warning(f"Unsupported file format: {file_extension}")
            return {
                "status": "error", 
                "content": "Not supported format"
            }
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Extrai texto
        if file_extension.lower() == ".pdf":
            parser = PDFParser(tmp_path)
            clean_text = parser.extract_text()
            clean_text = " ".join(clean_text)  # junta as páginas em uma única string
        elif file_extension.lower() == ".docx":
            parser = DocxParser(tmp_path)
            clean_text = parser.get_text()
        else:
            clean_text = ""

        os.remove(tmp_path)

        if not clean_text.strip():
            return {"status": "error", "message": "Arquivo vazio ou não suportado"}

        # Embeddings e classificação
        query_embedding = embedder.generate_embeddings(clean_text)
        predicted_class, confidence, _ = vector_store.predict_class(query_embedding)

        # Log classification process
        classification_logger.info(f"Classifying document: {predicted_class}")
        
        # Extração com prompt específico
        prompt_engine = PromptEngine()
        extracted_data = prompt_engine.extract(predicted_class, clean_text)

        return {
            "status": "success",
            "predicted_class": predicted_class,
            "confidence": round(confidence, 4),
            "extracted_data": extracted_data
        }
    
    except Exception as e:
        # Comprehensive error logging
        error_logger.exception(f"Error processing upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal processing error"
        )