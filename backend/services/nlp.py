import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class NLPService:
    @staticmethod
    def extract_entities_and_relationships(text: str):
        """
        Uses Groq LLM to extract entities and relationships from text.
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
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured information from text into Knowledge Graphs. Output only JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-8b-8192",
                response_format={ "type": "json_object" }
            )
            
            raw_result = chat_completion.choices[0].message.content
            data = json.loads(raw_result)
            
            return NLPService._validate_and_clean(data)
            
        except Exception as e:
            print(f"Error in NLP extraction: {e}")
            return {"entities": [], "relationships": []}

    @staticmethod
    def _validate_and_clean(data: dict) -> dict:
        """
        Validates the structure and cleans names/types.
        """
        clean_data = {"entities": [], "relationships": []}
        
        if not isinstance(data, dict):
            return clean_data

        # Process entities
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

        # Process relationships
        relationships = data.get("relationships", [])
        if not isinstance(relationships, list):
            relationships = []
            
        for rel in relationships:
            if not isinstance(rel, dict) or "source" not in rel or "target" not in rel or "type" not in rel:
                continue
                
            source = str(rel["source"]).strip()
            target = str(rel["target"]).strip()
            rel_type = str(rel["type"]).strip()
            
            # Basic validation: source and target should be in existing entities
            if source.lower() in existing_entities and target.lower() in existing_entities:
                clean_data["relationships"].append({
                    "source": source,
                    "target": target,
                    "type": rel_type
                })
        
        return clean_data
