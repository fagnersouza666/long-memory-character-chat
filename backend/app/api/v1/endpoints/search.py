from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from prisma import Prisma
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas.search import SearchQuery, SearchResponse, SearchResult
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search(
    search_query: SearchQuery,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Buscar semanticamente em documentos e avaliações"""
    try:
        # Verificar permissões para o workspace especificado
        if search_query.workspace_id:
            workspace_user = await db.workspaceuser.find_unique(
                where={
                    "userId_workspaceId": {
                        "userId": current_user.id,
                        "workspaceId": search_query.workspace_id
                    }
                }
            )
            
            if not workspace_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to search in this workspace"
                )
        
        results = []
        
        if search_query.search_type == "semantic":
            results = await semantic_search(search_query, current_user, db)
        elif search_query.search_type == "keyword":
            results = await keyword_search(search_query, current_user, db)
        elif search_query.search_type == "hybrid":
            results = await hybrid_search(search_query, current_user, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid search type. Valid types: semantic, keyword, hybrid"
            )
        
        # Limitar resultados
        results = results[:search_query.limit]
        
        return SearchResponse(
            query=search_query.query,
            results=results,
            total_results=len(results),
            search_type=search_query.search_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")

async def semantic_search(search_query: SearchQuery, current_user: UserModel, db: Prisma):
    """Busca semântica usando embeddings"""
    # Esta é uma implementação simplificada
    # Na prática, isso usaria um modelo de embedding real e um armazenamento vetorial
    
    results = []
    
    # Buscar chunks de documentos relevantes
    document_chunks = await get_relevant_document_chunks(search_query, current_user, db)
    results.extend(document_chunks)
    
    # Buscar avaliações relevantes
    evaluations = await get_relevant_evaluations(search_query, current_user, db)
    results.extend(evaluations)
    
    # Ordenar por score (simulação)
    results.sort(key=lambda x: x.score, reverse=True)
    
    return results

async def keyword_search(search_query: SearchQuery, current_user: UserModel, db: Prisma):
    """Busca por palavras-chave usando TF-IDF"""
    results = []
    
    # Buscar documentos com palavras-chave
    document_results = await keyword_search_documents(search_query, current_user, db)
    results.extend(document_results)
    
    # Buscar avaliações com palavras-chave
    evaluation_results = await keyword_search_evaluations(search_query, current_user, db)
    results.extend(evaluation_results)
    
    # Ordenar por score
    results.sort(key=lambda x: x.score, reverse=True)
    
    return results

async def hybrid_search(search_query: SearchQuery, current_user: UserModel, db: Prisma):
    """Busca híbrida combinando busca semântica e por palavras-chave"""
    # Realizar busca semântica
    semantic_results = await semantic_search(search_query, current_user, db)
    
    # Realizar busca por palavras-chave
    keyword_results = await keyword_search(search_query, current_user, db)
    
    # Combinar resultados (simplificado)
    combined_results = combine_search_results(semantic_results, keyword_results)
    
    # Ordenar por score combinado
    combined_results.sort(key=lambda x: x.score, reverse=True)
    
    return combined_results

async def get_relevant_document_chunks(search_query: SearchQuery, current_user: UserModel, db: Prisma):
    """Obter chunks de documentos relevantes"""
    # Esta função seria implementada com um armazenamento vetorial real
    # Para esta implementação, simulamos a recuperação
    
    # Construir condição WHERE para documentos acessíveis
    where = build_document_access_filter(current_user, search_query.workspace_id)
    
    # Buscar documentos
    documents = await db.document.find_many(
        where=where,
        include={
            "chunks": True
        }
    )
    
    # Simular busca semântica
    results = []
    for doc in documents:
        for chunk in doc.chunks:
            # Simular score baseado em similaridade (aleatório para demonstração)
            score = np.random.random()
            
            # Aplicar filtros se especificados
            if search_query.filters:
                if not matches_filters(chunk, search_query.filters):
                    continue
            
            results.append(SearchResult(
                id=f"doc_{doc.id}_chunk_{chunk.id}",
                content=chunk.content,
                metadata={
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "file_type": doc.fileType,
                    "author_id": doc.authorId,
                    "upload_date": doc.uploadDate.isoformat(),
                    "workspace_id": doc.workspaceId
                },
                score=score,
                source_type="document"
            ))
    
    return results

async def get_relevant_evaluations(search_query: SearchQuery, current_user: UserModel, db: Prisma):
    """Obter avaliações relevantes"""
    # Construir condição WHERE para avaliações acessíveis
    where = build_evaluation_access_filter(current_user)
    
    # Buscar avaliações
    evaluations = await db.evaluation.find_many(where=where)
    
    # Simular busca semântica
    results = []
    for eval in evaluations:
        # Simular score baseado em similaridade (aleatório para demonstração)
        score = np.random.random()
        
        # Aplicar filtros se especificados
        if search_query.filters:
            if not matches_filters(eval, search_query.filters):
                continue
        
        # Obter informações do funcionário
        employee = await db.user.find_unique(
            where={
                "id": eval.employeeId
            }
        )
        
        evaluator = None
        if eval.evaluatorId:
            evaluator = await db.user.find_unique(
                where={
                    "id": eval.evaluatorId
                }
            )
        
        results.append(SearchResult(
            id=f"eval_{eval.id}",
            content=eval.content,
            metadata={
                "evaluation_id": eval.id,
                "employee_id": eval.employeeId,
                "employee_name": employee.username if employee else "Unknown",
                "evaluator_id": eval.evaluatorId,
                "evaluator_name": evaluator.username if evaluator else "Unknown",
                "period": eval.period,
                "score": eval.score,
                "created_at": eval.createdAt.isoformat()
            },
            score=score,
            source_type="evaluation"
        ))
    
    return results

async def keyword_search_documents(search_query: SearchQuery, current_user: UserModel, db: Prisma):
    """Buscar documentos por palavras-chave"""
    # Construir condição WHERE para documentos acessíveis
    where = build_document_access_filter(current_user, search_query.workspace_id)
    
    # Buscar documentos
    documents = await db.document.find_many(
        where=where,
        include={
            "chunks": True
        }
    )
    
    # Extrair conteúdo para TF-IDF
    documents_content = []
    document_chunk_map = []
    
    for doc in documents:
        for chunk in doc.chunks:
            documents_content.append(chunk.content)
            document_chunk_map.append((doc, chunk))
    
    if not documents_content:
        return []
    
    # Calcular TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents_content)
    
    # Calcular similaridade com a query
    query_vector = vectorizer.transform([search_query.query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Criar resultados
    results = []
    for i, similarity in enumerate(similarities):
        if similarity > 0:  # Apenas resultados com alguma relevância
            doc, chunk = document_chunk_map[i]
            
            # Obter informações do autor
            author = await db.user.find_unique(
                where={
                    "id": doc.authorId
                }
            )
            
            results.append(SearchResult(
                id=f"doc_{doc.id}_chunk_{chunk.id}",
                content=chunk.content,
                metadata={
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "file_type": doc.fileType,
                    "author_id": doc.authorId,
                    "author_name": author.username if author else "Unknown",
                    "upload_date": doc.uploadDate.isoformat(),
                    "workspace_id": doc.workspaceId
                },
                score=float(similarity),
                source_type="document"
            ))
    
    return results

async def keyword_search_evaluations(search_query: SearchQuery, current_user: UserModel, db: Prisma):
    """Buscar avaliações por palavras-chave"""
    # Construir condição WHERE para avaliações acessíveis
    where = build_evaluation_access_filter(current_user)
    
    # Buscar avaliações
    evaluations = await db.evaluation.find_many(where=where)
    
    # Extrair conteúdo para TF-IDF
    evaluations_content = []
    evaluation_map = []
    
    for eval in evaluations:
        evaluations_content.append(eval.content)
        evaluation_map.append(eval)
    
    if not evaluations_content:
        return []
    
    # Calcular TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(evaluations_content)
    
    # Calcular similaridade com a query
    query_vector = vectorizer.transform([search_query.query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Criar resultados
    results = []
    for i, similarity in enumerate(similarities):
        if similarity > 0:  # Apenas resultados com alguma relevância
            eval = evaluation_map[i]
            
            # Obter informações do funcionário
            employee = await db.user.find_unique(
                where={
                    "id": eval.employeeId
                }
            )
            
            evaluator = None
            if eval.evaluatorId:
                evaluator = await db.user.find_unique(
                    where={
                        "id": eval.evaluatorId
                    }
                )
            
            results.append(SearchResult(
                id=f"eval_{eval.id}",
                content=eval.content,
                metadata={
                    "evaluation_id": eval.id,
                    "employee_id": eval.employeeId,
                    "employee_name": employee.username if employee else "Unknown",
                    "evaluator_id": eval.evaluatorId,
                    "evaluator_name": evaluator.username if evaluator else "Unknown",
                    "period": eval.period,
                    "score": eval.score,
                    "created_at": eval.createdAt.isoformat()
                },
                score=float(similarity),
                source_type="evaluation"
            ))
    
    return results

def combine_search_results(semantic_results: List[SearchResult], keyword_results: List[SearchResult]):
    """Combinar resultados de busca semântica e por palavras-chave"""
    # Criar mapa de resultados por ID
    result_map = {}
    
    # Adicionar resultados semânticos
    for result in semantic_results:
        result_map[result.id] = {
            "result": result,
            "semantic_score": result.score,
            "keyword_score": 0.0
        }
    
    # Adicionar resultados por palavras-chave
    for result in keyword_results:
        if result.id in result_map:
            result_map[result.id]["keyword_score"] = result.score
        else:
            result_map[result.id] = {
                "result": result,
                "semantic_score": 0.0,
                "keyword_score": result.score
            }
    
    # Combinar scores (média simples)
    combined_results = []
    for item in result_map.values():
        combined_score = (item["semantic_score"] + item["keyword_score"]) / 2
        item["result"].score = combined_score
        combined_results.append(item["result"])
    
    return combined_results

def build_document_access_filter(current_user: UserModel, workspace_id: Optional[int] = None):
    """Construir filtro para documentos acessíveis"""
    where = {}
    
    if workspace_id:
        # Filtrar por workspace específico
        where["workspaceId"] = workspace_id
    else:
        # Filtrar por documentos acessíveis ao usuário
        if current_user.role == "admin":
            # Administradores podem ver todos os documentos
            pass
        else:
            # Outros usuários podem ver:
            # 1. Documentos pessoais (workspaceId = 0) que eles criaram
            # 2. Documentos em workspaces onde eles são membros
            where["OR"] = [
                {
                    "AND": [
                        {"workspaceId": 0},
                        {"authorId": current_user.id}
                    ]
                },
                {
                    "workspaceId": {
                        "in": []  # Seria preenchido com IDs de workspaces do usuário
                    }
                }
            ]
    
    return where

def build_evaluation_access_filter(current_user: UserModel):
    """Construir filtro para avaliações acessíveis"""
    where = {}
    
    if current_user.role == "admin":
        # Administradores podem ver todas as avaliações
        pass
    elif current_user.role == "manager":
        # Gerentes podem ver avaliações de funcionários do mesmo departamento
        where["employee"] = {
            "department": current_user.department
        }
    else:
        # Funcionários comuns só podem ver suas próprias avaliações
        where["employeeId"] = current_user.id
    
    return where

def matches_filters(item: Any, filters: dict):
    """Verificar se um item corresponde aos filtros especificados"""
    # Esta é uma implementação simplificada
    # Na prática, seria necessário verificar os metadados do item contra os filtros
    return True