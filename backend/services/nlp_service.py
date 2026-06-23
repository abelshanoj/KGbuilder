import json
import logging
from infrastructure.llm_provider import llm_provider
from utils.text_normalizer import normalize_entity

logger = logging.getLogger(__name__)


class NLPService:

    @staticmethod
    def generate_response(
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant.",
        model: str = "llama-3.1-8b-instant",
        max_chars: int = 12000
    ) -> str:
        """
        Generic wrapper for LLM calls.
        Handles truncation and error safety.
        """

        try:
            # Prevent context overflow
            safe_prompt = prompt[:max_chars]

            return llm_provider.generate_text(
                prompt=safe_prompt,
                system_prompt=system_prompt,
                model=model
            )

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "Failed to generate response."

    @staticmethod
    def extract_entities_and_relationships(text: str) -> dict:
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
                system_prompt="You extract structured knowledge graphs. Output ONLY valid JSON."
            )

            data = json.loads(raw_result)
            return NLPService._validate_and_clean(data)

        except Exception as e:
            logger.error(f"Error in NLP extraction: {e}")
            return {"entities": [], "relationships": []}

    @staticmethod
    def _validate_and_clean(data: dict) -> dict:
        clean_data = {"entities": [], "relationships": []}

        if not isinstance(data, dict):
            return clean_data

        entities = data.get("entities", [])
        existing_entities = set()

        for ent in entities if isinstance(entities, list) else []:
            if not isinstance(ent, dict):
                continue

            raw_name = str(ent.get("name", "")).strip()
            name = normalize_entity(raw_name)  
            ent_type = str(ent.get("type", "")).strip()

            if not name or not ent_type:
                continue

            if name in existing_entities:
                continue

            existing_entities.add(name)

            clean_data["entities"].append({
                "name": name,  
                "type": ent_type.lower().strip(),
                "description": str(ent.get("description", "")).strip()
            })

        relationships = data.get("relationships", [])

        for rel in relationships if isinstance(relationships, list) else []:
            if not isinstance(rel, dict):
                continue

            source = normalize_entity(rel.get("source", ""))
            target = normalize_entity(rel.get("target", ""))
            rel_type = str(rel.get("type", "")).strip().lower()

            if source in existing_entities and target in existing_entities:
                clean_data["relationships"].append({
                    "source": source,
                    "target": target,
                    "type": rel_type
                })

        return clean_data

    @staticmethod
    def generate_rag_response(query: str, context: str) -> str:

        prompt = f"""
        You are a precise AI assistant.

        Answer the question using ONLY the provided context.

        If the answer is not present, respond exactly with:
        "I cannot answer this based on the provided documents."

        ---------------------
        CONTEXT:
        {context[:10000]}
        ---------------------

        QUESTION:
        {query}

        INSTRUCTIONS:
        - Start directly with the answer (no introductions). There shouldn't be any text other than the answer
        - DO NOT mention "context", "graph", or "relationships"
        - DO NOT say "According to..."
        - DO NOT explain where the answer comes from
        - Be concise and factual
        - Use bullet points if multiple facts are present
        - Do not hallucinate or infer beyond the given data

        ANSWER:
        """

        return NLPService.generate_response(
            prompt=prompt,
            system_prompt="You answer strictly from given context.",
        )