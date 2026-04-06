from supabase import create_client, Client
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseAdapter:
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.warning("Supabase credentials missing. Supabase operations will fail.")
            self.client = None
            return

        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        self.bucket = "documents"

    def get_workspaces(self, user_id: str):
        res = self.client.table("workspaces").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
        return res.data

    def get_workspace(self, workspace_id: str, user_id: str):
        res = self.client.table("workspaces").select("*").eq("id", workspace_id).eq("user_id", user_id).single().execute()
        return res.data

    def get_documents(self, user_id: str, workspace_id: str):
        res = self.client.table("documents").select("*").eq("user_id", user_id).eq("workspace_id", workspace_id).execute()
        return res.data

    def get_document(self, document_id: str):
        res = self.client.table("documents").select("*").eq("id", document_id).single().execute()
        return res.data
        
    def get_job(self, job_id: str):
        res = self.client.table("documents").select("*").eq("job_id", job_id).single().execute()
        return res.data

    def create_workspace(self, user_id: str, name: str):
        res = self.client.table("workspaces").insert({
            "user_id": user_id, "name": name, "doc_count": 0, "entity_count": 0
        }).execute()
        return res.data[0]

    def create_document(self, user_id: str, workspace_id: str, file_name: str, status: str = "pending", job_id: str = None):
        res = self.client.table("documents").insert({
            "user_id": user_id, "workspace_id": workspace_id, "file_name": file_name, 
            "status": status, "job_id": job_id
        }).execute()
        return res.data[0]

    def update_document_job(self, document_id: str, status: str, job_id: str = None, error: str = None):
        update_data = {"status": status}
        if job_id: update_data["job_id"] = job_id
        if error is not None: update_data["error"] = error
        
        res = self.client.table("documents").update(update_data).eq("id", document_id).execute()
        return res.data

    def update_workspace_stats(self, workspace_id: str, user_id: str, doc_count: int, entity_count: int):
        res = self.client.table("workspaces").update({
            "doc_count": doc_count, "entity_count": entity_count, "updated_at": "now()"
        }).eq("id", workspace_id).eq("user_id", user_id).execute()
        return res.data

    # Storage operations
    def upload_file(self, file_path: str, storage_path: str):
        with open(file_path, "rb") as f:
            res = self.client.storage.from_(self.bucket).upload(storage_path, f)
        return res

    def download_file(self, storage_path: str, local_path: str):
        res = self.client.storage.from_(self.bucket).download(storage_path)
        with open(local_path, "wb") as f:
            f.write(res)
        return local_path

    # Vector operations
    def store_embeddings(self, document_id: str, workspace_id: str, embeddings_data: list):
        """Stores a list of dictionaries with content and vector embedding"""
        if not embeddings_data: return
        
        # Add metadata to each chunk
        records = []
        for d in embeddings_data:
            records.append({
                "document_id": document_id,
                "workspace_id": workspace_id,
                "content": d["content"],
                "embedding": d["embedding"]
            })
            
        # Bulk insert
        self.client.table("document_embeddings").insert(records).execute()

    def query_embeddings(self, workspace_id: str, query_vector: list, limit: int = 5):
        # Requires match_embeddings RPC in Supabase manually if standard eq doesn't work,
        # but using the vector API:
        res = self.client.rpc("match_embeddings", {
            "query_embedding": query_vector,
            "filter_workspace_id": workspace_id,
            "match_count": limit
        }).execute()
        return res.data

supabase_adapter = SupabaseAdapter()
