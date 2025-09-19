from fastapi import APIRouter, File, Form, UploadFile
from typing import Optional
import os 
import tempfile
from services.docx_parser import DocxParser   
from services.pdf_parser import PDFParser

router = APIRouter()

@router.post("/upload")
async def upload_file(
    name: str = Form(...),                           
    file        : UploadFile = File(...)            
):
    # Get the file extension using os.path.splitext
    filename, file_extension = os.path.splitext(file        .filename)

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
        tmp.write(await file        .read())
        tmp_path = tmp.name # temporary file
    
    # Decide which parser to use
    if file_extension.lower() == '.pdf':
        parser = PDFParser(tmp_path)
        clen_text = parser.extract_text()
    elif file_extension.lower() == '.docx':
        reader = DocxParser(tmp_path)
        clen_text = reader.get_text()
    else:
        clen_text = "Not supported format"

    os.remove(tmp_path)

    return {
        "name": name,
        "file_name": file.filename,
        "file_extension": file_extension,
        "content":clen_text
    }