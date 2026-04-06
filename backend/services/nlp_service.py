import json
import logging
from infrastructure.llm_provider import llm_provider

logger = logging.getLogger(__name__)

class NLPService:
    @staticmethod
    def extract_entities_and_relationships(text: str) -> dict:
        """
        Uses LLMProvider to extract entities and relationships from text.
        Returns a validated dictionary with entities and relationships.
        """
        prompt = f"""
        Extract entities and relationships from the following text based on the provided schema.
        Return the output strictly in JSON format.

        Schema:
        {{
          "entities": [
            {{ "name": "string", "type": "string", "description": "brief context" }}
          ],
          "relationships": [
            {{ "source": "entity name", "target": "entity name", "type": "relationship type" }}
          ]
        }}

        Text:
        {text[:4000]}
        
        JSON Output:
        """

        try:
            raw_result = llm_provider.generate_json(
                prompt=prompt,
                system_prompt="You are an expert at extracting structured information from text into Knowledge Graphs. Output only JSON."
            )
            data = json.loads(raw_result)
            return NLPService._validate_and_clean(data)
            
        except Exception as e:
            logger.error(f"Error in NLP extraction: {e}")
            return {"entities": [], "relationships": []}

    @staticmethod
    def _validate_and_clean(data: dict) -> dict:
        """Validates the structure and cleans names/types."""
        clean_data = {"entities": [], "relationships": []}
        
        if not isinstance(data, dict):
            return clean_data

        entities = data.get("entities", [])
        if not isinstance(entities, list):
            entities = []
            
        existing_entities = set()
        for ent in entities:
            if not isinstance(ent, dict) or "name" not in ent or "type" not in ent:
                continue
            
            name = str(ent["name"]).strip()
            if not name:
                continue
                
            if name.lower() in existing_entities:
                continue
                
            existing_entities.add(name.lower())
            clean_data["entities"].append({
                "name": name,
                "type": str(ent["type"]).strip(),
                "description": str(ent.get("description", "")).strip()
            })

        relationships = data.get("relationships", [])
        if not isinstance(relationships, list):
            relationships = []
            
        for rel in relationships:
            if not isinstance(rel, dict) or "source" not in rel or "target" not in rel or "type" not in rel:
                continue
                
            source = str(rel["source"]).strip()
            target = str(rel["target"]).strip()
            rel_type = str(rel["type"]).strip()
            
            if source.lower() in existing_entities and target.lower() in existing_entities:
                clean_data["relationships"].append({
                    "source": source,
                    "target": target,
                    "type": rel_type
                })
        
        return clean_data

    @staticmethod
    def generate_rag_response(query: str, context: str) -> str:
        """Generates a contextualized response using RAG logic."""
        prompt = f"""
        Answer the following question based ONLY on the provided context. If the context does not contain the answer, say "I cannot answer this based on the provided documents."

        Context:
        {context}

        Question:
        {query}

        Answer:
        """
        try:
            return llm_provider.generate_text(
                prompt=prompt,
                system_prompt="You are a helpful assistant that answers questions accurately using only the given context.",
                model="llama-3.1-8b-instant"
            )
        except Exception as e:
            logger.error(f"Error in RAG generation: {e}")
            return "Failed to generate answer."
