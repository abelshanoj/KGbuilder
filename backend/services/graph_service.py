from infrastructure.neo4j_adapter import neo4j_adapter
import logging

logger = logging.getLogger(__name__)

class GraphService:
    @staticmethod
    def create_subgraph(workspace_id: str, entities: list, relationships: list):
        """Creates or merges subgraph in Neo4j."""
        try:
            neo4j_adapter.create_graph(workspace_id, entities, relationships)
        except Exception as e:
            logger.error(f"Failed to create subgraph: {e}")
            raise e

    @staticmethod
    def get_workspace_graph(workspace_id: str):
        return neo4j_adapter.get_workspace_graph(workspace_id)

    @staticmethod
    def retrieve_context(workspace_id: str, entities: list[str]) -> list[dict]:
        """Retrieves connections for particular entities to provide structured RAG context."""
        try:
            return neo4j_adapter.retrieve_context(workspace_id, entities, limit=20)
        except Exception as e:
            logger.error(f"Failed to retrieve graph context: {e}")
            return []

    @staticmethod
    def merge_entities(workspace_id: str, keep_name: str, delete_name: str):
        neo4j_adapter.merge_entities(workspace_id, keep_name, delete_name)

    @staticmethod
    def edit_entity(workspace_id: str, old_name: str, new_name: str, new_type: str, new_desc: str):
        neo4j_adapter.edit_entity(workspace_id, old_name, new_name, new_type, new_desc)
