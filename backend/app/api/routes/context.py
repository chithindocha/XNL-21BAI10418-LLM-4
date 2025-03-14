from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.auth import get_current_active_user
from app.services.vector_store import VectorStore
import json

router = APIRouter()

class Document(BaseModel):
    id: int
    content: str
    source: str
    timestamp: datetime

class DocumentCreate(BaseModel):
    content: str
    source: str

class DocumentResponse(BaseModel):
    id: int
    source: str
    timestamp: datetime

@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    current_user = Depends(get_current_active_user),
    vector_store: VectorStore = Depends()
):
    """
    Add a new document to the context store
    """
    try:
        await vector_store.add_document(
            content=document.content,
            source=document.source
        )
        return DocumentResponse(
            id=len(vector_store.metadata) - 1,
            source=document.source,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding document: {str(e)}"
        )

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    current_user = Depends(get_current_active_user),
    vector_store: VectorStore = Depends(),
    skip: int = 0,
    limit: int = 10
):
    """
    List all documents in the context store
    """
    try:
        documents = vector_store.metadata[skip:skip + limit]
        return [
            DocumentResponse(
                id=doc["id"],
                source=doc["source"],
                timestamp=datetime.fromisoformat(doc["timestamp"])
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user = Depends(get_current_active_user),
    vector_store: VectorStore = Depends()
):
    """
    Delete a document from the context store
    """
    try:
        await vector_store.delete_document(document_id)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user),
    vector_store: VectorStore = Depends()
):
    """
    Upload a document file to the context store
    """
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
        
        # Parse content based on file type
        if file.filename.endswith('.json'):
            data = json.loads(content_str)
            # Handle different JSON structures
            if isinstance(data, list):
                for item in data:
                    await vector_store.add_document(
                        content=json.dumps(item),
                        source=f"{file.filename}:{item.get('id', 'unknown')}"
                    )
            else:
                await vector_store.add_document(
                    content=content_str,
                    source=file.filename
                )
        else:
            # Handle plain text files
            await vector_store.add_document(
                content=content_str,
                source=file.filename
            )
        
        return {"message": "Document uploaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/search")
async def search_context(
    query: str,
    current_user = Depends(get_current_active_user),
    vector_store: VectorStore = Depends(),
    limit: int = 5
):
    """
    Search for relevant context using semantic search
    """
    try:
        results = await vector_store.get_relevant_context(query, k=limit)
        return {
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching context: {str(e)}"
        ) 