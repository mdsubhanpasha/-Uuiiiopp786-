"""
PASHA-NEURO-RAG FastAPI Service & Observability Instrumentation
Author: Mohammad Subhan Pasha
"""

import os
import time
import json
import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator

from neuro_rag.config import settings
from neuro_rag.ingestion.schemas import Document, Chunk, IngestionResponse
from neuro_rag.ingestion.parsers import DocumentParserFactory
from neuro_rag.ingestion.semantic_chunker import SemanticChunker
from neuro_rag.retrieval.vector_store import VectorStoreManager
from neuro_rag.retrieval.bm25_retriever import BM25Retriever
from neuro_rag.retrieval.hybrid_search import HybridSearchEngine
from neuro_rag.orchestration.graph import SelfCorrectingRAGGraph

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("neuro_rag.api")

# Global engine singletons
vector_store = VectorStoreManager()
bm25_retriever = BM25Retriever()
hybrid_engine = HybridSearchEngine(vector_store=vector_store, bm25_retriever=bm25_retriever)
rag_graph = SelfCorrectingRAGGraph(search_engine=hybrid_engine)
# Pass vector_store.generate_embeddings_batch to enable semantic sentence similarity splitting
semantic_chunker = SemanticChunker(embed_fn=vector_store.generate_embeddings_batch)

# Metrics
REQUEST_COUNT = Counter("neuro_rag_requests_total", "Total requests served", ["endpoint"])
INGESTED_DOCS_COUNT = Counter("neuro_rag_ingested_docs_total", "Total documents ingested", ["source_type"])
CHAT_LATENCY_HISTOGRAM = Histogram("neuro_rag_chat_latency_seconds", "Latency of RAG chat responses")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} by {settings.AUTHOR}")
    yield
    logger.info("Shutting down PASHA-NEURO-RAG service.")


app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    description=f"Self-Correcting Enterprise RAG System created by {settings.AUTHOR}",
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


class ChatRequest(BaseModel):
    query: str = Field(..., description="User query string")
    stream: bool = Field(default=True, description="Whether to stream response tokens")


class IngestUrlRequest(BaseModel):
    url: str
    source_type: str = "url"


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "author": settings.AUTHOR,
        "version": settings.VERSION,
        "docs": "/docs",
        "metrics": "/metrics"
    }


@app.post("/ingest", response_model=IngestionResponse)
async def ingest_document(
    file: Optional[UploadFile] = File(None),
    source_type: Optional[str] = Form(None),
    raw_text: Optional[str] = Form(None),
    url: Optional[str] = Form(None)
):
    REQUEST_COUNT.labels(endpoint="/ingest").inc()
    temp_path = None
    try:
        stype = source_type or "pdf"

        if file:
            filename = file.filename or "upload_doc"
            if filename.endswith(".pdf"):
                stype = "pdf"
            elif filename.endswith(".docx"):
                stype = "docx"

            temp_dir = "/tmp/pasha_neuro_rag_ingest"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, "wb") as f:
                content_bytes = await file.read()
                f.write(content_bytes)

            doc = DocumentParserFactory.parse(stype, temp_path)
        elif url:
            doc = DocumentParserFactory.parse("url", url)
            stype = "url"
        elif raw_text:
            doc = DocumentParserFactory.parse("notion", raw_text)
            stype = "notion"
        else:
            raise HTTPException(status_code=400, detail="Must provide either file upload, url, or raw_text.")

        chunks = semantic_chunker.chunk_document(doc)
        if not chunks:
            raise HTTPException(status_code=400, detail="Failed to chunk document or document content empty.")

        vector_store.index_chunks(chunks)
        bm25_retriever.index_chunks(chunks)

        INGESTED_DOCS_COUNT.labels(source_type=stype).inc()
        total_tokens = sum(c.metadata.token_count for c in chunks)

        return IngestionResponse(
            status="success",
            doc_id=doc.doc_id,
            source_name=doc.metadata.source_name,
            chunk_count=len(chunks),
            total_tokens=total_tokens,
            message=f"Successfully ingested {doc.metadata.source_name} with {len(chunks)} semantic chunks."
        )

    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    REQUEST_COUNT.labels(endpoint="/chat").inc()
    start_time = time.time()

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if not request.stream:
        # Non-streaming full response
        rag_result = rag_graph.run(request.query)
        latency = time.time() - start_time
        CHAT_LATENCY_HISTOGRAM.observe(latency)

        return {
            "query": request.query,
            "answer": rag_result["final_answer"],
            "is_grounded": rag_result["is_grounded"],
            "groundedness_score": rag_result["groundedness_score"],
            "critique_score": rag_result["critique_score"],
            "critique_feedback": rag_result["critique_feedback"],
            "iterations": rag_result["iteration"],
            "citations": rag_result["citations"],
            "latency_seconds": round(latency, 3),
            "author": settings.AUTHOR
        }

    # SSE Streaming response generator
    async def event_generator():
        try:
            rag_result = rag_graph.run(request.query)
            final_answer = rag_result["final_answer"]

            # Stream tokens
            words = final_answer.split(" ")
            for w in words:
                data = json.dumps({"type": "token", "content": w + " "})
                yield f"data: {data}\n\n"

            # Metadata payload
            meta_payload = {
                "type": "metadata",
                "is_grounded": rag_result["is_grounded"],
                "groundedness_score": rag_result["groundedness_score"],
                "critique_score": rag_result["critique_score"],
                "critique_feedback": rag_result["critique_feedback"],
                "iterations": rag_result["iteration"],
                "citations": rag_result["citations"],
                "author": settings.AUTHOR
            }
            yield f"data: {json.dumps(meta_payload)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            err_data = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {err_data}\n\n"
        finally:
            latency = time.time() - start_time
            CHAT_LATENCY_HISTOGRAM.observe(latency)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
