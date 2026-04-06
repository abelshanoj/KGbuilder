import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from infrastructure.neo4j_adapter import neo4j_adapter

from api.workspaces import router as workspace_router
from api.graph import router as graph_router
from api.jobs import router as jobs_router
from api.query import router as query_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Neo4j
    logger.info("Starting up: Initializing database...")
    try:
         neo4j_adapter.init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    yield
    # Shutdown: Close Neo4j driver
    logger.info("Shutting down: Closing database connection...")
    neo4j_adapter.close()

app = FastAPI(title="Knowledge Graph Builder API (Modular)", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://k-gbuilder.vercel.app",
        "https://k-gbuilder-git-main-abel-shanojs-projects.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workspace_router)
app.include_router(graph_router)
app.include_router(jobs_router)
app.include_router(query_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
