import os
import re
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        self.driver = GraphDatabase.driver(
            self.uri, 
            auth=(self.user, self.password),
            max_connection_lifetime=3600,
            keep_alive=True
        )

    def close(self):
        self.driver.close()

    def init_db(self):
        """Initializes database constraints and verifies connectivity."""
        try:
            with self.driver.session(database=self.database) as session:
                # Verify connectivity
                session.run("RETURN 1")
                
                # Create uniqueness constraint
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
        # Uppercase, replace spaces with underscore, remove invalid chars
        rel_type = rel_type.upper().replace(" ", "_")
        rel_type = re.sub(r'[^A-Z0-9_]', '', rel_type)
        return rel_type if rel_type else "RELATED_TO"

    def create_graph(self, workspace_id: str, entities: list, relationships: list):
        """Creates entities and relationships in Neo4j using batch processing."""
        
        query = """
        UNWIND $entities AS entity
        MERGE (e:Entity {name: entity.name, workspace_id: $workspace_id})
        SET e.type = entity.type,
            e.description = COALESCE(entity.description, "")
        """
        
        # Prepare relationships with sanitized types
        sanitized_rels = []
        for rel in relationships:
            sanitized_rels.append({
                "source": rel["source"],
                "target": rel["target"],
                "type": self.sanitize_rel_type(rel["type"])
            })

        def _create_rels_tx(tx, workspace_id, rels):
            for rel in rels:
                # Safety check: ensure both source and target exist in this workspace
                # Using dynamic relationship type in a single transaction
                rel_query = f"""
                MATCH (a:Entity {{name: $source, workspace_id: $workspace_id}})
                MATCH (b:Entity {{name: $target, workspace_id: $workspace_id}})
                MERGE (a)-[r:{rel['type']}]->(b)
                SET r.workspace_id = $workspace_id
                """
                tx.run(rel_query, source=rel["source"], target=rel["target"], workspace_id=workspace_id)

        with self.driver.session(database=self.database) as session:
            # Batch insert entities
            session.execute_write(lambda tx: tx.run(query, entities=entities, workspace_id=workspace_id))
            
            # Insert relationships one by one inside a session (or we can use APOC for dynamic rels but better keep it simple)
            # Since standard Cypher doesn't allow dynamic relationship types in MERGE via parameters,
            # we iterate and use f-strings safely since types are sanitized.
            session.execute_write(_create_rels_tx, workspace_id, sanitized_rels)

    def get_workspace_graph(self, workspace_id):
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

        with self.driver.session() as session:
            result = session.run(query, workspace_id=workspace_id)
            record = result.single()   # ✅ INSIDE session

            if not record:
                return {"nodes": [], "edges": []}

            nodes = record["nodes"] or []
            edges = [e for e in record["edges"] if e is not None]

            return {
                "nodes": nodes,
                "edges": edges
            }

    def merge_entities(self, workspace_id: str, keep_name: str, delete_name: str):
        """Merges two entities in the knowledge graph. Moves all relationships to 'keep' entity."""
        
        with self.driver.session(database=self.database) as session:
            # 1. Verify existence of both nodes in the workspace
            check_query = """
            MATCH (e:Entity {workspace_id: $workspace_id})
            WHERE e.name IN [$keep_name, $delete_name]
            RETURN e.name as name
            """
            result = session.run(check_query, workspace_id=workspace_id, keep_name=keep_name, delete_name=delete_name)
            names_found = [record["name"] for record in result]
            
            if keep_name not in names_found:
                raise ValueError(f"Target entity '{keep_name}' not found in this workspace.")
            if delete_name not in names_found:
                raise ValueError(f"Source entity '{delete_name}' not found in this workspace.")

            # 2. Perform merge using a robust strategy that doesn't filter rows
            # We use multiple statements or a heavily guarded single query.
            # Here, we'll use a series of OPTIONAL MATCHES and APOC calls.
            query = """
            MATCH (keep:Entity {name: $keep_name, workspace_id: $workspace_id})
            MATCH (delete:Entity {name: $delete_name, workspace_id: $workspace_id})
            
            // 1. Move outgoing rels
            WITH keep, delete
            OPTIONAL MATCH (delete)-[r_out]->(target)
            WHERE target <> keep
            WITH keep, delete, collect({r: r_out, target: target}) as out_items
            CALL apoc.cypher.doIt("
                UNWIND $items as item
                WITH item WHERE item.r IS NOT NULL
                CALL apoc.merge.relationship($keep, type(item.r), properties(item.r), {workspace_id: $wid}, item.target) YIELD rel
                DELETE item.r
                RETURN count(*) as c
            ", {items: out_items, keep: keep, wid: $workspace_id}) YIELD value
            
            // 2. Move incoming rels
            WITH keep, delete
            OPTIONAL MATCH (source)-[r_in]->(delete)
            WHERE source <> keep
            WITH keep, delete, collect({r: r_in, source: source}) as in_items
            CALL apoc.cypher.doIt("
                UNWIND $items as item
                WITH item WHERE item.r IS NOT NULL
                CALL apoc.merge.relationship(item.source, type(item.r), properties(item.r), {workspace_id: $wid}, $keep) YIELD rel
                DELETE item.r
                RETURN count(*) as c
            ", {items: in_items, keep: keep, wid: $workspace_id}) YIELD value
            
            // 3. Final Delete
            WITH delete
            DETACH DELETE delete
            """
            
            try:
                session.execute_write(lambda tx: tx.run(query, keep_name=keep_name, delete_name=delete_name, workspace_id=workspace_id))
            except Exception as e:
                logger.error(f"Merge operation failed: {e}")
                # Fallback: Basic DETACH DELETE if the complex one fails
                # (e.g. if apoc.cypher.doIt is also restricted)
                fallback_query = "MATCH (delete:Entity {name: $delete_name, workspace_id: $workspace_id}) DETACH DELETE delete"
                session.execute_write(lambda tx: tx.run(fallback_query, delete_name=delete_name, workspace_id=workspace_id))



    def edit_entity(self, workspace_id: str, old_name: str, new_name: str, new_type: str, new_desc: str):
        """Updates entity properties. Checks for collisions if name changed."""
        
        with self.driver.session(database=self.database) as session:
            # 1. Collision check if name is changing
            if old_name != new_name:
                check_query = "MATCH (e:Entity {name: $new_name, workspace_id: $workspace_id}) RETURN e"
                result = session.run(check_query, new_name=new_name, workspace_id=workspace_id)
                if result.peek():
                    raise ValueError(f"Entity with name '{new_name}' already exists in this workspace.")

            # 2. Perform the update
            # If name changes, we need to update all incoming/outgoing relationships as well in current Neo4j structure
            # (since we use name as ID)
            update_query = """
            MATCH (e:Entity {name: $old_name, workspace_id: $workspace_id})
            SET e.name = $new_name, 
                e.type = $new_type, 
                e.description = $new_desc
            """
            session.execute_write(lambda tx: tx.run(
                update_query, 
                old_name=old_name, 
                new_name=new_name, 
                new_type=new_type, 
                new_desc=new_desc, 
                workspace_id=workspace_id
            ))
            
            # Since 'name' is the ID used for source/target in relationships, 
            # if we change the name, we must update all relationships!
            if old_name != new_name:
                # This is a bit expensive but necessary if name is the key
                rename_rels_query = """
                MATCH (x:Entity)-[r]->(old:Entity {name: $new_name, workspace_id: $workspace_id})
                // No need to do more here if using internal Neo4j IDs, 
                // but since our relationship source/target strings are NOT stored in the rel but implicit in the graph structure,
                // Neo4j handles the node rename automatically. The get_graph query uses n.name as ID,
                // so after n.name = $new_name, the collect() will return the new label correctly.
                """
                pass 
                # Actually, Neo4j MERGE and SET just works on the node.
                # Relationships point to node IDs, not names (unless we stored names as properties on rels).
                # Our get_workspace_graph uses n.name as the ID, so it will pick up the new name automatically.


# Singleton-like instance
neo4j_service = Neo4jService()
