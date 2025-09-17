from fastapi import APIRouter, File, Form, UploadFile
from typing import Optional

router = APIRouter()

@router.post("/upload")
def upload_file(
    nome: str = Form(...),                      # campo de texto obrigatório
    descricao: Optional[str] = Form(None),      # campo de texto opcional
    arquivo: UploadFile = File(...)             # upload de arquivo obrigatório
):
    return {
        "campos_recebidos": {
            "nome": nome,
            "descricao": descricao,
            "arquivo_nome": arquivo.filename
        }
    }