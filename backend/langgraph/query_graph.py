from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END
from services.nlp_service import NLPService
from services.vector_service import VectorService
from services.graph_service import GraphService
import json
import logging
from services.ranking_service import ranking_service
from infrastructure.llm_provider import llm_provider
from utils.text_normalizer import normalize_entity

logging.basicConfig(level=logging.INFO)
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

    prompt = f"""
Extract key entity names from this query.

Return ONLY valid JSON:
{{"entities": ["entity1", "entity2"]}}

Rules:
- Use base/singular forms
- Avoid plurals

Query:
{state['query']}
"""
    try:
        raw_res = llm_provider.generate_json(
            prompt,
            system_prompt="You extract normalized entity names."
        )

        data = json.loads(raw_res)
        entities = data.get("entities", [])

        if not isinstance(entities, list):
            entities = []

        entities = list(set([
            normalize_entity(e) for e in entities if isinstance(e, str)
        ]))

    except Exception as e:
        logger.warning(f"Failed to extract entities from query: {e}")
        entities = []

    logger.info(f"Normalized Query entities: {entities}")
    return {"extracted_entities": entities}

def retrieve_vectors(state: QueryState):
    logger.info("Retrieving vectors")
    chunks = VectorService.retrieve_similar_chunks(state["workspace_id"], state["query"])
    chunks = list(set(chunks)) if chunks else []
    return {"vector_context": chunks}

def rank_chunks(state: QueryState):
    logger.info("Ranking chunks using CrossEncoder")

    chunks = state.get("vector_context", [])
    if not chunks:
        return {"vector_context": []}

    ranked_chunks = ranking_service.rank(
        query=state["query"],
        chunks=chunks,
        top_k=3
    )

    return {"vector_context": ranked_chunks}

def summarize_chunks(state: QueryState):
    logger.info("Summarizing ranked chunks")

    chunks = state.get("vector_context", [])
    if not chunks:
        return {"vector_context": []}

    context = "\n\n".join(chunks)

    prompt = f"""
        You are a precise technical summarizer.

        Extract only the most relevant facts needed to answer the query.

        Query:
        {state['query']}

        Context:
        {context}

        Rules:
        - Keep it concise
        - Remove redundancy
        - Preserve factual accuracy
        - No explanations, only useful facts
    """

    summary = NLPService.generate_response(prompt)

    return {"vector_context": [summary]}

def retrieve_graph(state: QueryState):
    logger.info("Retrieving graph context")
    if not state.get("extracted_entities"):
        return {"graph_context": []}
    context = GraphService.retrieve_context(state["workspace_id"], state["extracted_entities"])
    logger.info(f"Retrieved graph context: {context}")
    return {"graph_context": context}


def merge_and_answer(state: QueryState):
    logger.info("Merging context and generating answer")
    vc = "\n".join(state["vector_context"]) if state.get("vector_context") else "None"
    gc = json.dumps(state["graph_context"]) if state.get("graph_context") else "None"
    logger.info(f"Vector context: {vc}")
    logger.info(f"Graph context: {gc}")
    logger.info(f"Query: {state['query']}")
    
    merged = f"--- Vector Matches ---\n{vc}\n\n--- Graph Relationships ---\n{gc}"
    
    ans = NLPService.generate_rag_response(state["query"], merged)
    
    logger.info(f"Answer: {ans}")
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
builder.add_node("rank_chunks", rank_chunks)            
builder.add_node("summarize_chunks", summarize_chunks)  
builder.add_node("retrieve_graph", retrieve_graph)
builder.add_node("merge_and_answer", merge_and_answer)

builder.set_entry_point("extract_query_entities")

builder.add_edge("extract_query_entities", "retrieve_vectors")
builder.add_edge("retrieve_vectors", "rank_chunks")      
builder.add_edge("rank_chunks", "summarize_chunks")         
builder.add_edge("summarize_chunks", "retrieve_graph")      
builder.add_edge("retrieve_graph", "merge_and_answer")
builder.add_edge("merge_and_answer", END)

query_pipeline = builder.compile()