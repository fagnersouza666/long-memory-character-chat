from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SearchQuery(BaseModel):
    query: str
    workspace_id: Optional[int] = None
    search_type: str = "semantic"  # "semantic", "keyword", or "hybrid"
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    source_type: str  # "document", "evaluation", "note"

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_type: str