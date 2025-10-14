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

@router.post("/documents/{document_id}/category")
def update_document_category(
    document_id: str, 
    category_data: Dict[str, str], 
    db: Session = Depends(get_db)
):
    try:
        # Find the document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update the category
        # Find or create a classification for the document
        classification = document.classification
        if not classification:
            classification = Classification(document_id=document.id)
            db.add(classification)
        
        classification.category = category_data.get('category')
        db.commit()
        
        return {"message": "Category updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating document category: {str(e)}")
