from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END
from services.nlp_service import NLPService
from services.vector_service import VectorService
from services.graph_service import GraphService
import json
import logging

logger = logging.getLogger(__name__)

class QueryState(TypedDict):
    workspace_id: str
    query: str
    extracted_entities: Optional[list[str]]
    vector_context: Optional[list[str]]
    graph_context: Optional[list[dict]]
    merged_context: Optional[str]
    sources: Optional[list[dict]]
    answer: Optional[str]
    
def extract_query_entities(state: QueryState):
    logger.info(f"Extracting entities for query: {state['query']}")
    prompt = f"Extract key entity names from this query. Return ONLY a JSON format: {{'entities': ['name1', 'name2']}}. Query: {state['query']}"
    from infrastructure.llm_provider import llm_provider
    try:
        raw_res = llm_provider.generate_json(prompt, system_prompt="You extract concepts and names from a question into JSON.")
        data = json.loads(raw_res)
        entities = data.get("entities", [])
        if not isinstance(entities, list):
            entities = []
    except Exception as e:
        logger.warning(f"Failed to extract entities from query: {e}")
        entities = []
    return {"extracted_entities": entities}

def retrieve_vectors(state: QueryState):
    logger.info("Retrieving vectors")
    chunks = VectorService.retrieve_similar_chunks(state["workspace_id"], state["query"])
    return {"vector_context": chunks}

def retrieve_graph(state: QueryState):
    logger.info("Retrieving graph context")
    if not state.get("extracted_entities"):
        return {"graph_context": []}
    context = GraphService.retrieve_context(state["workspace_id"], state["extracted_entities"])
    return {"graph_context": context}
    
def merge_and_answer(state: QueryState):
    logger.info("Merging context and generating answer")
    vc = "\n".join(state["vector_context"]) if state.get("vector_context") else "None"
    gc = json.dumps(state["graph_context"]) if state.get("graph_context") else "None"
    merged = f"--- Vector Matches ---\n{vc}\n\n--- Graph Relationships ---\n{gc}"
    
    ans = NLPService.generate_rag_response(state["query"], merged)
    
    # Construct sources list
    sources = []
    if state.get("vector_context"):
        for chunk in state["vector_context"]:
            sources.append({"content": chunk, "document_name": "Vector Store Match"})
    if state.get("graph_context"):
        for gc_item in state["graph_context"]:
            sources.append({"content": json.dumps(gc_item), "document_name": "Knowledge Graph Relationship"})
    
    return {"merged_context": merged, "answer": ans, "sources": sources}

builder = StateGraph(QueryState)
builder.add_node("extract_query_entities", extract_query_entities)
builder.add_node("retrieve_vectors", retrieve_vectors)
builder.add_node("retrieve_graph", retrieve_graph)
builder.add_node("merge_and_answer", merge_and_answer)

builder.set_entry_point("extract_query_entities")

# In LangGraph, we can run nodes in parallel (edges from same node), but let's keep it sequential for simplicity
# or parallelize vector and graph
builder.add_edge("extract_query_entities", "retrieve_vectors")
builder.add_edge("retrieve_vectors", "retrieve_graph")
builder.add_edge("retrieve_graph", "merge_and_answer")
builder.add_edge("merge_and_answer", END)

query_pipeline = builder.compile()
