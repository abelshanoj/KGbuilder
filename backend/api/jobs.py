from fastapi import APIRouter, Depends, HTTPException
from core.security import get_current_user
from infrastructure.supabase_adapter import supabase_adapter
from models.schemas import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    
    # Fetch job info (which is stored in documents table)
    document = supabase_adapter.get_job(job_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Basic security check - ensure user owns the document
    if document.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return JobResponse(
        job_id=job_id,
        status=document.get("status", "unknown"),
        document_id=document.get("id"),
        error=document.get("error")
    )
