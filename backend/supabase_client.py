import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.url or not self.key:
            raise RuntimeError("Supabase credentials missing")

        self.client: Client = create_client(self.url, self.key)

    def get_workspaces(self, user_id: str):
        response = (
            self.client
            .table("workspaces")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return response.data

    def get_workspace(self, workspace_id: str, user_id: str):
        response = (
            self.client
            .table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return response.data

    def create_workspace(self, user_id: str, name: str):
        response = (
            self.client
            .table("workspaces")
            .insert({
                "user_id": user_id,
                "name": name,
                "doc_count": 0,
                "entity_count": 0
            })
            .execute()
        )
        return response.data[0]

    def update_workspace_stats(self, workspace_id: str, user_id: str, doc_count: int, entity_count: int):
        response = (
            self.client
            .table("workspaces")
            .update({
                "doc_count": doc_count,
                "entity_count": entity_count,
                "updated_at": "now()"
            })
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data

# Singleton-like instance
supabase_service = SupabaseService()
