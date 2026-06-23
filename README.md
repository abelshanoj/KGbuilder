KGbuilder

# DB Structure

User A
 ├── Workspace 1
 │    ├── Doc 1
 │    │      ├── Doc1 embeddings(1..n)
 │    │      ├── Doc1 entities
 │    │      ├── Doc1 relations
 │    ├── Doc 2
 │    │      ├── Doc1 embeddings(1..n)
 │    │      ├── Doc1 entities
 │    │      ├── Doc1 relations
 │
 ├── Workspace 2
 |       ├── Doc 3
 |           ├── Doc1 embeddings(1..n)
 |           ├── Doc1 entities
 |           ├── Doc1 relations
 User B
 ├── Workspace 1
        ├── Doc 4
        │     ├── Doc1 embeddings(1..n)
        │     ├── Doc1 entities
        │     ├── Doc1 relations
        ├── Doc 5
            ├── Doc1 embeddings(1..n)
            ├── Doc1 entities
            ├── Doc1 relations

# Schemas

auth.users(id, email, providers, created_at, last_signin_at)

public.workspaces (id, name, user_id, created_at, updated_at, doc_count, entity_count)

public.documents (id, workspace_id, user_id, file_name, created_at);

public.document_embeddings (id, document_id, workspace_id, content text, embedding vector(384), created_at);

- RPC (Remote Procedure Call):
Python → call RPC function → DB does everything → returns result

create or replace function match_embeddings (
  query_embedding vector(384),
  filter_workspace_id uuid,
  match_count int DEFAULT 5
) returns table (
  id uuid,
  content text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    de.id,
    de.content,
    1 - (de.embedding <=> query_embedding) as similarity
  from document_embeddings de
  where de.workspace_id = filter_workspace_id
  order by de.embedding <=> query_embedding
  limit match_count;
end;
$$;

Other options: FAISS: A local vector search library, Pineocone(Standalone Vector DB)


# Backend

Query Graph

        User Query
            │
            ▼
    [Preprocess Query]
            │
            ▼
    [Generate Embedding]
            │
            ▼
    [Vector Search (RPC)]
            │
            ▼
    [Retrieve Top Chunks]
            │
            ▼
    [Reranking of chunks]
            │
            ▼
    [Summarizing context]
            │
            ▼
    [Graph Retrieval]
            │
            ▼
    [Context Assembly]
            │
            ▼
    [LLM Response Generation]
            │
            ▼
         Response

Worker

        FastAPI
            │
            ▼
Create Job in DB
            │
            ▼
    Job Queue (implicit)
            │
            ▼
    Worker Process
            │
            ▼
    ingestion_graph.execute()
            │
            ▼
    Updates DB


Ingestion Graph
        
        (API)
            │
            ▼
[Create Document Entry]
            │
            ▼
    [Upload File]
            │
            ▼

    Background Job    
            │
            ▼
    Load Document    
            │
            ▼
    Chunk Text       
            │
            ▼
    Generate Embedding 
            │
            ▼
    Store Embeddings   
            │
            ▼
    Entity Extraction (LLM)    
            │
            ▼
    Relationship Extraction    
            │
            ▼
    Store Graph Data   
            │
            ▼
    Update Workspace   



Full Architecture

Signup
   │
   ▼
Login
   │
   ▼
Create Workspace
   │
   ▼
Upload Document
   │
   ▼
Backend Supabase (store metadata + file)
   │
   ▼
Worker picks job
   │
   ▼
ingestion_graph
   │
   ├── embeddings → document_embeddings
   ├── graph → graph DB
   │
   ▼
Document status = completed
   │
   ▼
Displays Knowledge Graph using Cytoscape.js
   │
   ▼
User asks query
   │
   ▼
query_graph
   │
   ├── embedding
   ├── RPC (match_embeddings)
   ├── retrieve chunks
   │
   ▼
LLM generates answer
   │
   ▼
Frontend shows answer