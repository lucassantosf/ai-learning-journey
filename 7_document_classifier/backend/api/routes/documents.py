from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from api.core.database import SessionLocal
from api.core.models import Document, Classification
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/documents/history")
def get_document_history(db: Session = Depends(get_db)):
    try:
        # Fetch documents from the database
        documents = db.query(Document).order_by(Document.created_at.desc()).all()
        
        # Transform documents into the required format
        document_history = [
            {
                "id": str(doc.id),
                "filename": doc.title,
                "current_category": doc.classification.category if doc.classification else "uncategorized",
                "upload_date": doc.created_at.isoformat() if doc.created_at else datetime.utcnow().isoformat()
            }
            for doc in documents
        ]
        
        return document_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document history: {str(e)}")