from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from supabase_client import supabase_service
from utils.auth import get_current_user
import uuid

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

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    return supabase_service.get_workspaces(user_id)

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_service.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(workspace_data: WorkspaceCreate, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    return supabase_service.create_workspace(user_id, workspace_data.name)

@router.get("/{workspace_id}/graph")
async def get_workspace_graph(workspace_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    # Verify ownership before fetching graph
    workspace = supabase_service.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    from database import neo4j_service
    return neo4j_service.get_workspace_graph(workspace_id)

# Additional workspace routes like delete or update can be added here
