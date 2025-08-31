import os
import shutil
from datetime import datetime


def create_directories():
    """Create necessary directories for the RAG system"""
    directories = [
        "docs/company",
        "docs/evaluations",
        "docs/processed",
        "rag_components",
        "database"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def save_uploaded_file(uploaded_file, destination_dir):
    """Save an uploaded file to the specified directory"""
    file_path = os.path.join(destination_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def generate_metadata(file_path, additional_metadata=None):
    """Generate metadata for a document"""
    stat = os.stat(file_path)
    
    metadata = {
        "source": file_path,
        "title": os.path.basename(file_path),
        "size": stat.st_size,
        "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "file_type": os.path.splitext(file_path)[1].lower()
    }
    
    if additional_metadata:
        metadata.update(additional_metadata)
    
    return metadata


def format_citations(source_documents):
    """Format source documents as citations"""
    citations = []
    for i, doc in enumerate(source_documents, 1):
        citation = f"{i}. {doc.metadata.get('title', 'Documento')} "
        if 'page' in doc.metadata:
            citation += f"(p. {doc.metadata['page']}) "
        if 'source' in doc.metadata:
            citation += f"[{doc.metadata['source']}]"
        citations.append(citation)
    
    return citations