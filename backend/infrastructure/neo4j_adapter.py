import logging
import re
from neo4j import GraphDatabase
from core.config import settings

logger = logging.getLogger(__name__)

class Neo4jAdapter:
    def __init__(self):
        if not settings.NEO4J_URI:
            logger.warning("NEO4J_URI is not set. Neo4j operations will fail.")
            self.driver = None
            return

        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
        
        self.driver = GraphDatabase.driver(
            self.uri, 
            auth=(self.user, self.password),
            max_connection_lifetime=3600,
            keep_alive=True
        )

    def close(self):
        if self.driver:
            self.driver.close()

    def init_db(self):
        """Initializes database constraints and verifies connectivity."""
        if not self.driver: return
        try:
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
                session.run("""
                    CREATE CONSTRAINT entity_workspace_name_unique IF NOT EXISTS
                    FOR (e:Entity) REQUIRE (e.name, e.workspace_id) IS UNIQUE
                """)
            logger.info("Neo4j initialized successfully with constraints.")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
            raise

    def sanitize_rel_type(self, rel_type: str) -> str:
        """Sanitizes relationship type for Neo4j."""
        rel_type = rel_type.upper().replace(" ", "_")
        rel_type = re.sub(r'[^A-Z0-9_]', '', rel_type)
        return rel_type if rel_type else "RELATED_TO"

    def create_graph(self, workspace_id: str, entities: list, relationships: list):
        """Creates entities and relationships in Neo4j idempotently."""
        if not self.driver: return

        # Idempotent node creation
        node_query = """
        UNWIND $entities AS entity
        MERGE (e:Entity {name: entity.name, workspace_id: $workspace_id})
        ON CREATE SET e.type = entity.type, e.description = COALESCE(entity.description, "")
        ON MATCH SET e.type = entity.type, e.description = COALESCE(entity.description, "")
        """
        
        sanitized_rels = []
        for rel in relationships:
            sanitized_rels.append({
                "source": rel["source"],
                "target": rel["target"],
                "type": self.sanitize_rel_type(rel["type"])
            })

        def _create_rels_tx(tx, w_id, rels):
            for rel in rels:
                # Idempotent relationship creation using MERGE
                rel_query = f"""
                MATCH (a:Entity {{name: $source, workspace_id: $workspace_id}})
                MATCH (b:Entity {{name: $target, workspace_id: $workspace_id}})
                MERGE (a)-[r:{rel['type']}]->(b)
                SET r.workspace_id = $workspace_id
                """
                tx.run(rel_query, source=rel["source"], target=rel["target"], workspace_id=w_id)

        with self.driver.session(database=self.database) as session:
            session.execute_write(lambda tx: tx.run(node_query, entities=entities, workspace_id=workspace_id))
            session.execute_write(_create_rels_tx, workspace_id, sanitized_rels)

    def get_workspace_graph(self, workspace_id):
        if not self.driver: return {"nodes": [], "edges": []}
        query = """
        MATCH (n:Entity {workspace_id: $workspace_id})
        OPTIONAL MATCH (n)-[r]->(m:Entity {workspace_id: $workspace_id})
        WITH n, r, m
        RETURN 
            collect(DISTINCT {
                id: n.name,
                label: n.name,
                type: n.type,
                description: n.description
            }) AS nodes,
            collect(DISTINCT CASE WHEN r IS NOT NULL THEN {
                source: n.name,
                target: m.name,
                label: type(r)
            } END) AS edges
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, workspace_id=workspace_id)
            record = result.single()
            if not record: return {"nodes": [], "edges": []}
            nodes = record["nodes"] or []
            edges = [e for e in record["edges"] if e is not None]
            return {"nodes": nodes, "edges": edges}

    def merge_entities(self, workspace_id: str, keep_name: str, delete_name: str):
        if not self.driver: return
        with self.driver.session(database=self.database) as session:
            check_query = """
            MATCH (e:Entity {workspace_id: $workspace_id})
            WHERE e.name IN [$keep_name, $delete_name]
            RETURN e.name as name
            """
            result = session.run(check_query, workspace_id=workspace_id, keep_name=keep_name, delete_name=delete_name)
            names_found = [record["name"] for record in result]
            if keep_name not in names_found:
                raise ValueError(f"Target entity '{keep_name}' not found.")
            if delete_name not in names_found:
                raise ValueError(f"Source entity '{delete_name}' not found.")

            query = """
            MATCH (keep:Entity {name: $keep_name, workspace_id: $workspace_id})
            MATCH (delete:Entity {name: $delete_name, workspace_id: $workspace_id})
            WITH keep, delete
            OPTIONAL MATCH (delete)-[r_out]->(target) WHERE target <> keep
            WITH keep, delete, collect({r: r_out, target: target}) as out_items
            CALL apoc.cypher.doIt("UNWIND $items as item WITH item WHERE item.r IS NOT NULL CALL apoc.merge.relationship($keep, type(item.r), properties(item.r), {workspace_id: $wid}, item.target) YIELD rel DELETE item.r RETURN count(*) as c", {items: out_items, keep: keep, wid: $workspace_id}) YIELD value as v1
            WITH keep, delete
            OPTIONAL MATCH (source)-[r_in]->(delete) WHERE source <> keep
            WITH keep, delete, collect({r: r_in, source: source}) as in_items
            CALL apoc.cypher.doIt("UNWIND $items as item WITH item WHERE item.r IS NOT NULL CALL apoc.merge.relationship(item.source, type(item.r), properties(item.r), {workspace_id: $wid}, $keep) YIELD rel DELETE item.r RETURN count(*) as c", {items: in_items, keep: keep, wid: $workspace_id}) YIELD value as v2
            WITH delete DETACH DELETE delete
            """
            try:
                session.execute_write(lambda tx: tx.run(query, keep_name=keep_name, delete_name=delete_name, workspace_id=workspace_id))
            except Exception as e:
                logger.error(f"Merge operation failed via APOC: {e}")
                fallback_query = "MATCH (delete:Entity {name: $delete_name, workspace_id: $workspace_id}) DETACH DELETE delete"
                session.execute_write(lambda tx: tx.run(fallback_query, delete_name=delete_name, workspace_id=workspace_id))

    def edit_entity(self, workspace_id: str, old_name: str, new_name: str, new_type: str, new_desc: str):
        if not self.driver: return
        with self.driver.session(database=self.database) as session:
            if old_name != new_name:
                check_query = "MATCH (e:Entity {name: $new_name, workspace_id: $workspace_id}) RETURN e"
                result = session.run(check_query, new_name=new_name, workspace_id=workspace_id)
                if result.peek():
                    raise ValueError(f"Entity with name '{new_name}' already exists.")
            update_query = """
            MATCH (e:Entity {name: $old_name, workspace_id: $workspace_id})
            SET e.name = $new_name, e.type = $new_type, e.description = $new_desc
            """
            session.execute_write(lambda tx: tx.run(
                update_query, old_name=old_name, new_name=new_name, new_type=new_type, new_desc=new_desc, workspace_id=workspace_id
            ))

    def retrieve_context(self, workspace_id: str, entity_names: list, limit: int = 50):
        """Retrieves subgraph neighborhood context for a list of entities."""
        if not self.driver: return []
        query = """
        MATCH (n:Entity {workspace_id: $workspace_id})
        WHERE n.name IN $entity_names
        OPTIONAL MATCH (n)-[r]-(m:Entity {workspace_id: $workspace_id})
        RETURN n.name AS entity, n.type AS type, n.description AS description, 
               collect(DISTINCT {rel: type(r), connected_to: m.name})[0..$limit] AS connections
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, workspace_id=workspace_id, entity_names=entity_names, limit=limit)
            return [dict(record) for record in result]

neo4j_adapter = Neo4jAdapter()
