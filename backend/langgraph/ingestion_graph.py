from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from services.document_service import DocumentService
from services.nlp_service import NLPService
from services.vector_service import VectorService
from services.graph_service import GraphService
import logging

logger = logging.getLogger(__name__)

class IngestionState(TypedDict):
    workspace_id: str
    document_id: str
    storage_path: str
    ext: str
    text: Optional[str]
    chunks: Optional[list[str]]
    extraction: Optional[dict]

def fetch_and_chunk(state: IngestionState):
    logger.info(f"[{state['document_id']}] Fetching and chunking")
    text = DocumentService.fetch_and_process_file(state["storage_path"], state["ext"])
    chunks = DocumentService.chunk_text(text)
    return {"text": text, "chunks": chunks}

def extract_entities(state: IngestionState):
    logger.info(f"[{state['document_id']}] Extracting entities via LLM")
    extraction = NLPService.extract_entities_and_relationships(state["text"])
    return {"extraction": extraction}

def embed_and_store(state: IngestionState):
    logger.info(f"[{state['document_id']}] Embedding and storing vectors")
    VectorService.embed_and_store_chunks(state["document_id"], state["workspace_id"], state["chunks"])
    return {}

def store_graph(state: IngestionState):
    logger.info(f"[{state['document_id']}] Storing graph in Neo4j")
    GraphService.create_subgraph(
        state["workspace_id"], 
        state["extraction"]["entities"], 
        state["extraction"]["relationships"]
    )
    return {}

builder = StateGraph(IngestionState)
builder.add_node("fetch_and_chunk", fetch_and_chunk)
builder.add_node("extract_entities", extract_entities)
builder.add_node("embed_and_store", embed_and_store)
builder.add_node("store_graph", store_graph)

builder.set_entry_point("fetch_and_chunk")
builder.add_edge("fetch_and_chunk", "extract_entities")
builder.add_edge("extract_entities", "embed_and_store")
builder.add_edge("embed_and_store", "store_graph")
builder.add_edge("store_graph", END)

ingestion_pipeline = builder.compile()
