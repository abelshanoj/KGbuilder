import logging
import traceback
from infrastructure.supabase_adapter import supabase_adapter
from infrastructure.neo4j_adapter import neo4j_adapter
from langgraph.ingestion_graph import ingestion_pipeline

logger = logging.getLogger(__name__)

def process_document_task(job_id: str, workspace_id: str, user_id: str, document_id: str, storage_path: str, ext: str):
    """
    Background job to process an uploaded document asynchronously.
    Executes LangGraph ingestion pipeline.
    """
    logger.info(f"Starting job {job_id} for document {document_id}")
    
    # 1. Update status to processing
    try:
        supabase_adapter.update_document_job(document_id, status="processing", job_id=job_id)
    except Exception as e:
        logger.error(f"Failed to update document status to processing: {e}")
        # Continue execution anyway, but log
        
    try:
        # 2. Prepare state for LangGraph
        initial_state = {
            "workspace_id": workspace_id,
            "document_id": document_id,
            "storage_path": storage_path,
            "ext": ext,
            "text": None,
            "chunks": None,
            "extraction": None
        }
        
        # 3. Run Pipeline
        final_state = ingestion_pipeline.invoke(initial_state)
        
        # 4. Update Workspace stats
        # To be accurate, let's fetch current counts
        workspace = supabase_adapter.get_workspace(workspace_id, user_id)
        if workspace:
            current_doc_count = workspace.get("doc_count", 0)
            
            # Recalculate entity count via Graph
            graph_data = neo4j_adapter.get_workspace_graph(workspace_id)
            new_entity_count = len(graph_data["nodes"]) if graph_data else 0
            
            supabase_adapter.update_workspace_stats(
                workspace_id, 
                user_id, 
                current_doc_count + 1, 
                new_entity_count
            )
            
        # 5. Mark as completed
        supabase_adapter.update_document_job(document_id, status="completed")
        logger.info(f"Successfully processed document {document_id}")

    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Job {job_id} failed for document {document_id}: {error_trace}")
        
        # Mark as failed
        try:
            # Optionally just save `str(e)` if trace is too long
            error_message = str(e)[:500] 
            supabase_adapter.update_document_job(document_id, status="failed", error=error_message)
        except Exception as inner_e:
            logger.error(f"Failed to save error status for {document_id}: {inner_e}")
            
        # Re-raise so RQ knows it failed and can apply retries
        raise e
