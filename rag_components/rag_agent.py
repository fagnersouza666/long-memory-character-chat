import streamlit as st
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os, datetime, pickle, time
import google.generativeai as genai
import anthropic
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from rag_components.document_processor import DocumentProcessor
from rag_components.query_processor import QueryProcessor
from rag_components.evaluation_manager import EvaluationManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RAGDocument:
    """RAGDocument class for storing text and metadata together."""
    
    def __init__(self, content, metadata, id):
        self.page_content = content
        self.metadata = metadata
        self.id = id


class RAGAgent:
    """RAGAgent class for Retrieval-Augmented Generation with documents and employee evaluations"""
    
    def __init__(
        self,
        model="gpt-3.5-turbo",
        embedding_model="text-embedding-3-small",
        summary_model="gpt-3.5-turbo",
    ):
        # Initialize the AI agent
        self.set_model(model)
        
        # initialize the summary model
        self.set_summary_model(summary_model)
        
        # Initialize the embeddings model
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # Initialize document processor
        self.document_processor = DocumentProcessor(embedding_model)
        
        # Initialize evaluation manager
        self.evaluation_manager = EvaluationManager()
        
        # Initialize vector store for documents
        self.vector_store = None
        
        # token and usage statistics
        self.total_cost = 0
        self.average_cost = 0
        self.total_tokens = 0
        self.average_tokens = 0
        self.current_memory_tokens = 0
        
        # NSFW filter
        self.nsfw = False
        
        # Load existing vector store if it exists
        self.load_vector_store()
    
    def load_vector_store(self):
        """Load existing vector store from disk"""
        try:
            if os.path.exists("faiss_index"):
                self.vector_store = self.document_processor.load_vector_store("faiss_index")
        except Exception as e:
            print(f"Could not load vector store: {e}")
            self.vector_store = None
    
    def save_vector_store(self):
        """Save vector store to disk"""
        if self.vector_store:
            self.document_processor.save_vector_store(self.vector_store, "faiss_index")
    
    def set_model(self, model="gpt-3.5-turbo") -> None:
        """Change the model the AI uses to generate responses."""
        self.model = model
        if "gpt" in self.model:
            api_key = os.getenv("OPENAI_API_KEY")
            self.agent = openai.OpenAI(
                api_key=api_key, base_url="https://api.openai.com/v1"
            )
        
        elif "gemini" in self.model:
            GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
            genai.configure(api_key=GOOGLE_API_KEY)
            self.agent = genai.GenerativeModel(model_name=self.model)
        
        elif "claude" in self.model:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            self.agent = anthropic.Anthropic(api_key=api_key)
        
        else:
            api_key = os.getenv("TOGETHER_API_KEY")
            self.agent = openai.OpenAI(
                api_key=api_key, base_url="https://api.together.xyz/v1"
            )
    
    def set_summary_model(self, summary_model="gpt-3.5-turbo") -> None:
        """Change the model the AI uses to summarize conversations."""
        self.summary_model = summary_model
        if "gpt" in self.summary_model:
            api_key = os.getenv("OPENAI_API_KEY")
            self.summary_agent = openai.OpenAI(
                api_key=api_key, base_url="https://api.openai.com/v1"
            )
        
        elif "gemini" in self.summary_model:
            GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
            genai.configure(api_key=GOOGLE_API_KEY)
            self.summary_agent = genai.GenerativeModel(model_name=self.summary_model)
        
        elif "claude" in self.summary_model:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            self.summary_agent = anthropic.Anthropic(api_key=api_key)
        
        else:
            api_key = os.getenv("TOGETHER_API_KEY")
            self.summary_agent = openai.OpenAI(
                api_key=api_key, base_url="https://api.together.xyz/v1"
            )
    
    def add_document(self, file_path, metadata=None) -> None:
        """Add a document to the RAG system"""
        try:
            # Process document
            documents = self.document_processor.process_document(file_path, metadata)
            
            # Add to vector store
            if self.vector_store is None:
                self.vector_store = self.document_processor.create_vector_store(documents)
            else:
                self.document_processor.add_documents_to_store(self.vector_store, documents)
            
            # Save vector store
            self.save_vector_store()
            
        except Exception as e:
            print(f"Error adding document: {e}")
    
    def add_evaluation(self, evaluation) -> None:
        """Add an employee evaluation to the RAG system"""
        try:
            # Add to evaluation manager
            self.evaluation_manager.add_evaluation(evaluation)
            
            # Convert only the new evaluation to document
            eval_documents = self.evaluation_manager.to_documents()
            # Get only the last added evaluation document
            new_eval_document = [eval_documents[-1]] if eval_documents else []
            
            # Add to vector store
            if self.vector_store is None:
                self.vector_store = self.document_processor.create_vector_store(new_eval_document)
            else:
                self.document_processor.add_documents_to_store(self.vector_store, new_eval_document)
            
            # Save vector store
            self.save_vector_store()
            
        except Exception as e:
            print(f"Error adding evaluation: {e}")
    
    def query(self, question, temperature=0.1, max_tokens=500) -> dict:
        """Query the RAG system for an answer to a question"""
        try:
            if self.vector_store is None:
                return {
                    "answer": "Nenhum documento foi adicionado ao sistema ainda.",
                    "source_documents": []
                }
            
            # Create query processor
            query_processor = QueryProcessor(self.vector_store, self.model)
            
            # Process query
            result = query_processor.query(question)
            
            return result
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "answer": "Ocorreu um erro ao processar sua pergunta.",
                "source_documents": []
            }
    
    def count_cost(self, result, model, summary=False) -> float:
        """Count the cost of the messages."""
        # cost is calculated as the number of tokens in the input and output times the cost per token
        if model.startswith("gpt-3"):
            input_cost = 0.0005 / 1000
            output_cost = 0.0015 / 1000
        elif model.startswith("gpt-4o-mini"):
            input_cost = 0.00015 / 1000
            output_cost = 0.0006 / 1000
        elif model.startswith("gpt-4"):
            input_cost = 0.01 / 1000
            output_cost = 0.03 / 1000
        elif "7b" or "8b" in model.lower() and "8x7b" not in model:
            input_cost = 0.0002 / 1000
            output_cost = 0.0002 / 1000
        elif "openchat/openchat-3.5-1210" in model.lower():
            input_cost = 0.0002 / 1000
            output_cost = 0.0002 / 1000
        elif "llama-2-13b" in model.lower():
            input_cost = 0.000225 / 1000
            output_cost = 0.000225 / 1000
        elif "13b" in model.lower():
            input_cost = 0.0003 / 1000
            output_cost = 0.0003 / 1000
        elif "gemini" in model:
            input_cost = 0
            output_cost = 0
        elif "claude" in model:
            input_cost = 0.00025 / 1000
            output_cost = 0.00125 / 1000
        else:
            print("Model not recognized")
            input_cost = 0
            output_cost = 0
        
        if "gemini" in model:
            # For simplicity, we'll estimate token counts
            input_tokens = 1000  # Estimate
            output_tokens = 200  # Estimate
        elif "claude" in model:
            input_tokens = result.usage.input_tokens
            output_tokens = result.usage.output_tokens
        else:
            input_tokens = result.usage.prompt_tokens
            output_tokens = result.usage.completion_tokens
        
        total_tokens = input_tokens + output_tokens
        lastest_cost = input_cost * input_tokens + output_cost * output_tokens
        
        self.total_cost += lastest_cost
        # determine the length of inputs and outputs
        self.average_cost = self.total_cost / 1 if self.total_tokens == 0 else self.total_cost / (self.total_tokens / 1000)
        self.total_tokens += total_tokens
        self.average_tokens = self.total_tokens / 1 if self.total_tokens == 0 else self.total_tokens / (self.total_tokens / 1000)
        if not summary:
            self.current_memory_tokens = total_tokens
        
        # calculate the cost
        return lastest_cost
    
    def format_messages_for_gemini(self, messages) -> list:
        """Format the messages for the Gemini model."""
        messages = [
            {"role": message["role"], "parts": message["content"]}
            for message in messages
        ]
        for message in messages:
            if message["role"] == "assistant":
                message["role"] = "model"
        return messages
    
    def clear_history(self):
        """Clear the RAG system history."""
        self.total_cost = 0
        self.total_tokens = 0
        self.current_memory_tokens = 0
        self.average_tokens = 0