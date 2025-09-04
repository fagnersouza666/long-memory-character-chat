from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import openai
import os


class QueryProcessor:
    """Process queries using RAG"""
    
    def __init__(self, vector_store, model="gpt-3.5-turbo"):
        self.vector_store = vector_store
        self.model = model
        # Removido o parâmetro temperature pois alguns modelos não o suportam
        self.llm = OpenAI(model_name=model, max_completion_tokens=500)
        
        # Create prompt template
        template = """
        Você é um assistente especializado em documentos corporativos e avaliações de funcionários.
        Use os seguintes documentos recuperados para responder à pergunta do usuário.
        Se a informação não estiver nos documentos, diga que não encontrou informações relevantes.
        
        Documentos recuperados:
        {context}
        
        Pergunta do usuário:
        {question}
        
        Resposta:
        """
        
        self.prompt_template = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
    
    def query(self, question, max_tokens=500):
        """Process a query and return answer with source documents"""
        # Atualizar o LLM com os parâmetros fornecidos (sem temperature)
        self.llm = OpenAI(model_name=self.model, max_completion_tokens=max_tokens)
        
        # Recriar a cadeia com o novo LLM
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
        
        result = self.qa_chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "source_documents": result["source_documents"]
        }