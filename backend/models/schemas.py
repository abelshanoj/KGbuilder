from pydantic import BaseModel
from typing import List, Optional, Any

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    user_id: str
    doc_count: int
    entity_count: int
    created_at: str
    updated_at: str

class DocumentResponse(BaseModel):
    id: str
    file_name: str
    user_id: str
    workspace_id: str
    created_at: str
    status: Optional[str] = "pending"
    job_id: Optional[str] = None
    error: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    document_id: str
    error: Optional[str] = None

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    description: Optional[str] = ""

class GraphEdge(BaseModel):
    source: str
    target: str
    label: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class QueryRequest(BaseModel):
    workspace_id: str
    query: str

class Source(BaseModel):
    content: str
    document_name: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
