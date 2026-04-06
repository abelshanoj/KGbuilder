from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.schemas import WorkspaceCreate, WorkspaceResponse, DocumentResponse
from infrastructure.supabase_adapter import supabase_adapter
from core.security import get_current_user
from services.graph_service import GraphService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    return supabase_adapter.get_workspaces(user_id)

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_adapter.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.get("/{workspace_id}/documents", response_model=List[DocumentResponse])
async def get_workspace_documents(workspace_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    documents = supabase_adapter.get_documents(user_id, workspace_id)
    if not documents:
        return []
    return documents

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(workspace_data: WorkspaceCreate, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    return supabase_adapter.create_workspace(user_id, workspace_data.name)

@router.get("/{workspace_id}/graph")
async def get_workspace_graph(workspace_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    # Verify ownership before fetching graph
    workspace = supabase_adapter.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return GraphService.get_workspace_graph(workspace_id)
