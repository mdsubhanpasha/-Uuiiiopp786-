"""Unit and Integration Test Suite for OmniRAG-Ops."""

import pytest

from src.agentic_rag import AgenticRAG
from src.corrective_rag import CorrectiveRAG
from src.graph_rag import GraphRAG
from src.hybrid_rag import HybridRAG
from src.naive_rag import NaiveRAG
from src.router import RAGRouter
from scripts.github_deploy import GitHubDeployer
from scripts.linkedin_poster import LinkedInPoster


@pytest.fixture
def corpus_path():
    """Fixture returning path to sample corpus JSON."""
    return "data/sample_corpus.json"


def test_naive_rag(corpus_path):
    """Test Naive RAG retrieval and generation."""
    rag = NaiveRAG(corpus_path=corpus_path)
    query = "Kubernetes container orchestration"

    results = rag.retrieve(query, top_k=2)
    assert len(results) > 0
    assert "score" in str(results[0]) or isinstance(results[0][1], float)

    gen = rag.generate(query)
    assert gen["paradigm"] == "Naive RAG"
    assert len(gen["retrieved_documents"]) > 0
    assert (
        "Kubernetes" in gen["response"]
        or "container" in gen["response"].lower()
    )


def test_hybrid_rag(corpus_path):
    """Test Hybrid RAG lexical + vector retrieval with RRF."""
    rag = HybridRAG(corpus_path=corpus_path)
    query = "BM25 vector search and cosine similarity"

    results = rag.retrieve(query, top_k=2)
    assert len(results) > 0

    gen = rag.generate(query)
    assert gen["paradigm"] == "Hybrid / Modular RAG"
    assert len(gen["retrieved_documents"]) > 0


def test_graph_rag(corpus_path):
    """Test Graph RAG multi-hop entity traversal."""
    rag = GraphRAG(corpus_path=corpus_path)
    query = "How is Istio related to Zero Trust?"

    search_res = rag.multi_hop_search(query, max_hops=2)
    assert "seed_entities" in search_res
    assert "traversed_relationships" in search_res

    gen = rag.generate(query)
    assert gen["paradigm"] == "Graph RAG"


def test_corrective_rag(corpus_path):
    """Test Corrective RAG confidence evaluation and web fallback."""
    crag = CorrectiveRAG(corpus_path=corpus_path, confidence_threshold=0.65)

    high_q = "Kubernetes Istio service mesh microservices"
    res_high = crag.generate(high_q)
    assert res_high["paradigm"] == "Corrective RAG (CRAG)"
    assert "confidence_score" in res_high

    low_q = "Unrelated quantum gravity superstring theory topic"
    res_low = crag.generate(low_q)
    assert res_low["fallback_triggered"] is True


def test_agentic_rag(corpus_path):
    """Test Agentic RAG multi-turn reasoning graph."""
    agent = AgenticRAG(corpus_path=corpus_path)
    query = "Decompose distributed microservices requirements"

    res = agent.run(query)
    assert res["paradigm"] == "Agentic RAG"
    assert len(res["sub_queries"]) > 0
    assert len(res["tool_calls"]) > 0


def test_router_classification(corpus_path):
    """Test RAG Router query intent classification."""
    router = RAGRouter(corpus_path=corpus_path)

    res_agentic = router.classify_query("Decompose multi-step workflow")
    assert res_agentic["paradigm"] == "Agentic RAG"

    res_graph = router.classify_query(
        "What is the relationship and topology link?"
    )
    assert res_graph["paradigm"] == "Graph RAG"

    res_crag = router.classify_query("Verify latest external update")
    assert res_crag["paradigm"] == "Corrective RAG (CRAG)"

    exec_res = router.route_and_execute("Kubernetes container orchestration")
    assert "selected_paradigm" in exec_res
    assert "latency_ms" in exec_res


def test_automation_scripts():
    """Test GitHub deployer and LinkedIn poster scripts."""
    deployer = GitHubDeployer()
    status = deployer.check_git_status()
    assert "has_changes" in status

    dry_deploy = deployer.deploy(dry_run=True)
    assert dry_deploy["status"] == "success"

    poster = LinkedInPoster()
    content = poster.generate_post_content()
    assert "OmniRAG-Ops" in content

    dry_post = poster.publish_post(dry_run=True)
    assert dry_post["status"] == "success"
