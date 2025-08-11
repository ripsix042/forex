import os
import numpy as np
from typing import List, Dict, Any, Optional
import pickle
import json

from ..config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    VECTOR_INDEX_NAME,
    EMBEDDING_DIMENSION,
    PROCESSED_DIR
)

# Optional imports with fallbacks
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

class VectorStore:
    def __init__(self):
        # Check for available dependencies
        self.use_pinecone = PINECONE_API_KEY is not None and PINECONE_API_KEY != "your_pinecone_api_key" and PINECONE_AVAILABLE
        self.use_embeddings = SENTENCE_TRANSFORMER_AVAILABLE
        self.use_faiss = FAISS_AVAILABLE
        
        # Initialize embedding model if available
        if self.use_embeddings:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Error initializing SentenceTransformer: {e}")
                self.use_embeddings = False
        
        if self.use_pinecone and self.use_embeddings:
            try:
                # Initialize Pinecone
                pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
                
                # Check if index exists, if not create it
                if VECTOR_INDEX_NAME not in pinecone.list_indexes():
                    pinecone.create_index(name=VECTOR_INDEX_NAME, dimension=EMBEDDING_DIMENSION)
                    
                self.index = pinecone.Index(VECTOR_INDEX_NAME)
            except Exception as e:
                print(f"Error initializing Pinecone: {e}")
                self.use_pinecone = False
        
        # Use local FAISS index as fallback if available
        if not self.use_pinecone and self.use_faiss and self.use_embeddings:
            try:
                self.faiss_index_path = os.path.join(PROCESSED_DIR, "faiss_index.bin")
                self.metadata_path = os.path.join(PROCESSED_DIR, "metadata.json")
                
                if os.path.exists(self.faiss_index_path):
                    self.faiss_index = faiss.read_index(self.faiss_index_path)
                    with open(self.metadata_path, 'r') as f:
                        self.metadata = json.load(f)
                else:
                    self.faiss_index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
                    self.metadata = {}
            except Exception as e:
                print(f"Error initializing FAISS: {e}")
                self.use_faiss = False
                self.metadata = {}
        elif not self.use_pinecone:
            # Simple dictionary-based storage as last resort
            self.metadata = {}
            self.simple_storage_path = os.path.join(PROCESSED_DIR, "simple_storage.json")
            if os.path.exists(self.simple_storage_path):
                try:
                    with open(self.simple_storage_path, 'r') as f:
                        self.metadata = json.load(f)
                except Exception as e:
                    print(f"Error loading simple storage: {e}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using SentenceTransformer"""
        if self.use_embeddings:
            try:
                return self.model.encode(text).tolist()
            except Exception as e:
                print(f"Error generating embedding: {e}")
                self.use_embeddings = False
        # Return empty embedding if model not available
        return [0.0] * EMBEDDING_DIMENSION
    
    def add_item(self, text: str, metadata: Dict[str, Any], id: Optional[str] = None) -> str:
        """Add an item to the vector store"""
        if not text.strip():
            print(f"Warning: Empty text for item, skipping")
            return id or "0"
            
        if self.use_pinecone and self.use_embeddings:
            try:
                embedding = self._get_embedding(text)
                if id is None:
                    id = str(len(self.metadata) if hasattr(self, 'metadata') else 0)
                self.index.upsert([(id, embedding, metadata)])
                return id
            except Exception as e:
                print(f"Error adding to Pinecone: {e}")
                self.use_pinecone = False
                # Fall through to alternatives
        
        if not self.use_pinecone and self.use_faiss and self.use_embeddings:
            try:
                if id is None:
                    id = str(len(self.metadata))
                
                embedding = self._get_embedding(text)
                # Add to FAISS index
                np_embedding = np.array([embedding], dtype=np.float32)
                self.faiss_index.add(np_embedding)
                
                # Store metadata
                self.metadata[id] = {
                    "text": text,
                    "metadata": metadata
                }
                
                # Save to disk
                try:
                    if not os.path.exists(PROCESSED_DIR):
                        os.makedirs(PROCESSED_DIR)
                    faiss.write_index(self.faiss_index, self.faiss_index_path)
                    with open(self.metadata_path, 'w') as f:
                        json.dump(self.metadata, f)
                except Exception as e:
                    print(f"Error saving FAISS index: {e}")
                
                return id
            except Exception as e:
                print(f"Error adding to FAISS: {e}")
                self.use_faiss = False
                # Fall through to simple storage
        
        # Simple storage as last resort
        if id is None:
            id = str(len(self.metadata))
        
        self.metadata[id] = {
            "text": text,
            "metadata": metadata
        }
        
        # Save simple storage
        try:
            if not os.path.exists(PROCESSED_DIR):
                os.makedirs(PROCESSED_DIR)
            with open(self.simple_storage_path, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            print(f"Error saving simple storage: {e}")
        
        return id
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar items in the vector store"""
        if not query.strip() or len(self.metadata) == 0:
            return []
            
        if self.use_pinecone and self.use_embeddings:
            try:
                query_embedding = self._get_embedding(query)
                results = self.index.query(query_embedding, top_k=top_k, include_metadata=True)
                return [{
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match["metadata"]
                } for match in results["matches"]]
            except Exception as e:
                print(f"Error searching Pinecone: {e}")
                self.use_pinecone = False
                # Fall through to alternatives
        
        if not self.use_pinecone and self.use_faiss and self.use_embeddings:
            try:
                query_embedding = self._get_embedding(query)
                np_embedding = np.array([query_embedding], dtype=np.float32)
                scores, indices = self.faiss_index.search(np_embedding, min(top_k, len(self.metadata)))
                
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx < len(self.metadata):
                        id_key = str(idx)
                        if id_key in self.metadata:
                            results.append({
                                "id": id_key,
                                "score": float(scores[0][i]),
                                "metadata": self.metadata[id_key]["metadata"],
                                "text": self.metadata[id_key]["text"]
                            })
                
                return results
            except Exception as e:
                print(f"Error searching FAISS: {e}")
                self.use_faiss = False
                # Fall through to simple search
        
        # Simple text-based search as last resort
        results = []
        query_terms = query.lower().split()
        
        for id, item in self.metadata.items():
            text = item["text"].lower()
            # Simple keyword matching
            score = sum(1 for term in query_terms if term in text) / max(len(query_terms), 1)
            
            if score > 0:
                results.append({
                    "id": id,
                    "score": score,
                    "metadata": item["metadata"],
                    "text": item["text"]
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

# Create a singleton instance
vector_store = VectorStore()