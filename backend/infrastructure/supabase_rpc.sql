"""
Postgres RPC needed for pgvector:

create or replace function match_embeddings (
  query_embedding vector(768),
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
"""
