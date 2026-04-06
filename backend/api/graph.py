from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
import shutil
import tempfile
import uuid

from infrastructure.supabase_adapter import supabase_adapter
from infrastructure.redis_adapter import redis_adapter
from core.security import get_current_user
from services.graph_service import GraphService
from workers.tasks import process_document_task
from langgraph.query_graph import query_pipeline

router = APIRouter(prefix="/graph", tags=["graph"])

@router.post("/{workspace_id}/upload")
async def upload_and_process(workspace_id: str, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    
    # Verify ownership
    workspace = supabase_adapter.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
    if workspace.get("doc_count", 0) >= 10:
        raise HTTPException(status_code=400, detail="Document limit reached (Max 10)")

    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    storage_path = f"{workspace_id}/{unique_filename}"

    # Save file temporarily to upload to Supabase Storage
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Upload to Supabase Storage
        supabase_adapter.upload_file(tmp_path, storage_path)
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload file to storage: {str(e)}")
    
    os.remove(tmp_path)

    # Note: the user requested document to have status='pending' and include a job_id.
    # We will generate a job ID prefix or let RQ generate it.
    
    # Store initial pending document row
    document = supabase_adapter.create_document(user_id, workspace_id, file.filename, status="pending")
    if not document:
        raise HTTPException(status_code=500, detail="Failed to create document record")

    document_id = document["id"]

    try:
        # Enqueue Job
        job = redis_adapter.enqueue_job(
            process_document_task,
            args=None,
            kwargs={
                "job_id": None, # Will be set by RQ job.id
                "workspace_id": workspace_id,
                "user_id": user_id,
                "document_id": document_id,
                "storage_path": storage_path,
                "ext": ext
            }
        )
        # Update kwargs job_id with actual job ID
        job.kwargs["job_id"] = job.id
        job.save_meta() # Optional, but we just pass job_id into supabase below
        
        # We need to tell Supabase about the job_id
        supabase_adapter.update_document_job(document_id, status="queued", job_id=job.id)
        
        # Provide job.id to the worker task payload by injecting it during task execution or reading it from current request context.
        # Note: In RQ, `get_current_job()` gives job.id inside the task, but we passed it as kwarg. Let's just rely on get_current_job.
        # Actually it's better if `enqueue_job` returns job, and we register `job.id` in DB.
        
    except Exception as e:
        supabase_adapter.update_document_job(document_id, status="failed", error=f"Queue error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to queue processing job: {str(e)}")

    return {"status": "queued", "job_id": job.id, "document_id": document_id}

@router.get("/{workspace_id}")
async def get_graph(workspace_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_adapter.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
    return GraphService.get_workspace_graph(workspace_id)

@router.put("/{workspace_id}/entity")
async def edit_entity(workspace_id: str, old_name: str, new_name: str, new_type: str, new_desc: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_adapter.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
    try:
        GraphService.edit_entity(workspace_id, old_name, new_name, new_type, new_desc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success"}

@router.post("/{workspace_id}/merge")
async def merge_entities(workspace_id: str, keep: str, delete: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_adapter.get_workspace(workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
    try:
        GraphService.merge_entities(workspace_id, keep, delete)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success"}


