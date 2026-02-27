from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from services.document import DocumentService
from services.nlp import NLPService
from database import neo4j_service
from supabase_client import supabase_service
from utils.auth import get_current_user
import os
import shutil
import tempfile

router = APIRouter(prefix="/graph", tags=["graph"])

@router.post("/{workspace_id}/upload")
async def upload_and_process(workspace_id: str, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    # Verify ownership
    workspace = supabase_service.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
    
    if workspace["doc_count"] >= 10:
        raise HTTPException(status_code=400, detail="Document limit reached (Max 10)")

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 1. Extract Text
        text = DocumentService.process_file(tmp_path)
        
        # 2. Extract Entities & Relationships
        extraction = NLPService.extract_entities_and_relationships(text)
        
        # 3. Store in Neo4j
        neo4j_service.create_graph(workspace_id, extraction["entities"], extraction["relationships"])
        
        # 4. Update Supabase Stats
        new_doc_count = workspace["doc_count"] + 1
        # Recalculate total entities
        graph_data = neo4j_service.get_workspace_graph(workspace_id)
        supabase_service.update_workspace_stats(workspace_id, user_id, new_doc_count, len(graph_data["nodes"]))
        
    finally:
        os.remove(tmp_path)

    return {"status": "success", "extracted": extraction}

@router.get("/{workspace_id}")
async def get_graph(workspace_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    # Verify ownership
    workspace = supabase_service.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
    return neo4j_service.get_workspace_graph(workspace_id)

@router.put("/{workspace_id}/entity")
async def edit_entity(workspace_id: str, old_name: str, new_name: str, new_type: str, new_desc: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_service.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
    neo4j_service.edit_entity(workspace_id, old_name, new_name, new_type, new_desc)
    return {"status": "success"}

@router.post("/{workspace_id}/merge")
async def merge_entities(workspace_id: str, keep: str, delete: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_service.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
    neo4j_service.merge_entities(workspace_id, keep, delete)
    return {"status": "success"}
