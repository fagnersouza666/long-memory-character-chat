import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import pickle
from datetime import datetime


class FAISSManager:
    """Manage FAISS vector store for enterprise documents"""
    
    def __init__(self, embedding_model="text-embedding-3-small", index_path="faiss_index"):
        self.embedding_model = embedding_model
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.index_path = index_path
        self.vector_store = None
        self.load_vector_store()
    
    def create_vector_store(self, documents):
        """Create a new FAISS vector store from documents"""
        if not documents:
            raise ValueError("No documents provided to create vector store")
        
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        return self.vector_store
    
    def add_documents(self, documents):
        """Add documents to the existing vector store or create a new one"""
        if not documents:
            raise ValueError("No documents provided to add")
        
        if self.vector_store is None:
            self.create_vector_store(documents)
        else:
            # Add documents to existing store
            self.vector_store.add_documents(documents)
        
        # Save the updated vector store
        self.save_vector_store()
    
    def similarity_search(self, query, k=5, filter=None):
        """Perform similarity search on the vector store"""
        if self.vector_store is None:
            return []
        
        if filter:
            return self.vector_store.similarity_search(query, k=k, filter=filter)
        else:
            return self.vector_store.similarity_search(query, k=k)
    
    def max_marginal_relevance_search(self, query, k=5, fetch_k=20):
        """Perform Max Marginal Relevance search to improve diversity"""
        if self.vector_store is None:
            return []
        
        return self.vector_store.max_marginal_relevance_search(query, k=k, fetch_k=fetch_k)
    
    def save_vector_store(self):
        """Save the vector store to disk"""
        if self.vector_store is not None:
            self.vector_store.save_local(self.index_path)
    
    def load_vector_store(self):
        """Load the vector store from disk"""
        if os.path.exists(self.index_path) and os.listdir(self.index_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.vector_store = None
        else:
            self.vector_store = None
    
    def delete_vector_store(self):
        """Delete the vector store from disk"""
        if os.path.exists(self.index_path):
            import shutil
            shutil.rmtree(self.index_path)
            self.vector_store = None
    
    def get_document_count(self):
        """Get the number of documents in the vector store"""
        if self.vector_store is None:
            return 0
        return len(self.vector_store.docstore._dict)
    
    def get_index_stats(self):
        """Get statistics about the vector store"""
        if self.vector_store is None:
            return {
                "document_count": 0,
                "last_updated": None
            }
        
        # Save stats to a file
        stats_file = f"{self.index_path}/stats.pkl"
        stats = {
            "document_count": len(self.vector_store.docstore._dict),
            "last_updated": datetime.now().isoformat()
        }
        
        return stats