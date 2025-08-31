import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import tempfile
import shutil
from datetime import datetime
import hashlib


class DocumentProcessor:
    """Process documents for RAG system"""
    
    def __init__(self, embedding_model="text-embedding-3-small"):
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def extract_metadata(self, file_path):
        """Extract basic metadata from a file"""
        stat = os.stat(file_path)
        
        metadata = {
            "source": file_path,
            "title": os.path.basename(file_path),
            "file_type": os.path.splitext(file_path)[1].lower(),
            "size": stat.st_size,
            "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "file_id": hashlib.md5(file_path.encode()).hexdigest()
        }
        
        return metadata
    
    def load_document(self, file_path):
        """Load document based on file extension"""
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        elif file_path.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        return loader.load()
    
    def process_document(self, file_path, metadata=None):
        """Process a document and return chunks with metadata"""
        # Load document
        documents = self.load_document(file_path)
        
        # Extract file metadata
        file_metadata = self.extract_metadata(file_path)
        
        # Add metadata to each document
        for doc in documents:
            # Add file metadata
            doc.metadata.update(file_metadata)
            
            # Add custom metadata
            if metadata:
                doc.metadata.update(metadata)
            
            # Add chunk index
            doc.metadata["total_chunks"] = len(documents)
        
        # Add chunk index to each document
        for i, doc in enumerate(documents):
            doc.metadata["chunk_index"] = i
        
        # Split document into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Update chunk metadata after splitting
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    def create_vector_store(self, documents):
        """Create a FAISS vector store from documents"""
        vector_store = FAISS.from_documents(documents, self.embeddings)
        return vector_store
    
    def add_documents_to_store(self, vector_store, documents):
        """Add documents to existing vector store"""
        vector_store.add_documents(documents)
        return vector_store
    
    def save_vector_store(self, vector_store, path):
        """Save vector store to disk"""
        vector_store.save_local(path)
    
    def load_vector_store(self, path):
        """Load vector store from disk"""
        return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)