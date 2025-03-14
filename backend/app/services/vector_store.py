from typing import List, Dict, Any
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_path = os.path.join(settings.VECTOR_DB_PATH, "faiss.index")
        self.metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
        
        # Create vector store directory if it doesn't exist
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        # Initialize or load the FAISS index
        self._initialize_index()
        
        # Load metadata
        self.metadata = self._load_metadata()

    def _initialize_index(self):
        """Initialize or load the FAISS index"""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            # Create a new index with the correct dimension
            dimension = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)
            faiss.write_index(self.index, self.index_path)

    def _load_metadata(self) -> List[Dict[str, Any]]:
        """Load metadata from file"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return []

    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)

    async def add_document(self, content: str, source: str):
        """
        Add a document to the vector store
        """
        try:
            # Generate embedding
            embedding = self.model.encode([content])[0]
            
            # Add to FAISS index
            self.index.add(np.array([embedding]).astype('float32'))
            
            # Add metadata
            self.metadata.append({
                "id": len(self.metadata),
                "content": content,
                "source": source,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Save changes
            faiss.write_index(self.index, self.index_path)
            self._save_metadata()
            
        except Exception as e:
            raise Exception(f"Error adding document to vector store: {str(e)}")

    async def get_relevant_context(
        self,
        query: str,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array([query_embedding]).astype('float32'),
                k
            )
            
            # Get relevant documents from metadata
            relevant_docs = []
            for idx in indices[0]:
                if idx < len(self.metadata):
                    relevant_docs.append(self.metadata[idx])
            
            return relevant_docs
            
        except Exception as e:
            raise Exception(f"Error retrieving context: {str(e)}")

    async def delete_document(self, doc_id: int):
        """
        Delete a document from the vector store
        """
        try:
            # Remove from metadata
            if 0 <= doc_id < len(self.metadata):
                self.metadata.pop(doc_id)
                
                # Rebuild index without the deleted document
                dimension = self.model.get_sentence_embedding_dimension()
                new_index = faiss.IndexFlatL2(dimension)
                
                # Re-add all documents except the deleted one
                for i, doc in enumerate(self.metadata):
                    embedding = self.model.encode([doc["content"]])[0]
                    new_index.add(np.array([embedding]).astype('float32'))
                
                # Replace old index with new one
                self.index = new_index
                faiss.write_index(self.index, self.index_path)
                self._save_metadata()
                
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}") 