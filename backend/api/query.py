from fastapi import APIRouter, Depends, HTTPException
from core.security import get_current_user
from infrastructure.supabase_adapter import supabase_adapter
from models.schemas import QueryRequest, QueryResponse
from langgraph.query_graph import query_pipeline
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])

@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    workspace = supabase_adapter.get_workspace(request.workspace_id, user_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    initial_state = {
        "workspace_id": request.workspace_id,
        "query": request.query
    }

    logger.info(f"Initial state: {initial_state}")
    
    try:
        final_state = query_pipeline.invoke(initial_state)
        # Using the new schema format
        return QueryResponse(
            answer=final_state.get("answer", "No answer generated."),
            sources=final_state.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")
