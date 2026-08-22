"""OmniRAG-Ops CLI and Demonstration Entry Point.

Provides a CLI interface to query individual RAG paradigms, auto-route
requests, or run comparative benchmarks across all 5 paradigms.
"""

import argparse
import json
import sys

from src.agentic_rag import AgenticRAG
from src.corrective_rag import CorrectiveRAG
from src.graph_rag import GraphRAG
from src.hybrid_rag import HybridRAG
from src.naive_rag import NaiveRAG
from src.router import RAGRouter


def print_banner() -> None:
    """Print OmniRAG-Ops ASCII Banner."""
    banner = (
        "=" * 80 + "\n"
        "             OMNIRAG-OPS: ENTERPRISE MULTI-TIER RETRIEVAL ENGINE\n"
        + "=" * 80 + "\n"
        "Paradigms: [1] Naive RAG | [2] Hybrid RAG | [3] Graph RAG | "
        "[4] Corrective RAG | [5] Agentic RAG\n"
        + "-" * 80 + "\n"
    )
    print(banner)


def run_demo() -> None:
    """Execute demonstration queries showcasing all 5 RAG paradigms."""
    print_banner()
    corpus_file = "data/sample_corpus.json"
    router = RAGRouter(corpus_path=corpus_file)

    sample_queries = [
        ("Simple Semantic Vector Search",
         "What is Kubernetes and container orchestration?"),
        ("Hybrid Keyword + Dense Search",
         "Explain BM25 lexical ranking with FAISS vector similarity"),
        ("Multi-Hop Graph Entity Search",
         "How is Istio related to Zero Trust security topology?"),
        ("Corrective RAG Evaluator & Fallback",
         "Verify latest updates on cloud security compliance for 2025"),
        ("Agentic Multi-Turn Reasoning",
         "Decompose complex architecture requirements step by step"),
    ]

    print("\n[+] RUNNING AUTOMATIC ROUTER DEMO ON SAMPLE QUERIES:\n")
    for category, query in sample_queries:
        print(f"\n--- Category: {category} ---")
        print(f"Query: '{query}'")
        res = router.route_and_execute(query)
        print(f"Selected Engine: {res['selected_paradigm']}")
        print(f"Routing Reason:  {res['routing_reasoning']}")
        print(f"Execution Time:  {res['latency_ms']} ms")
        print("-" * 60)
        print(res["engine_output"]["response"])
        print("=" * 80)


def main() -> None:
    """Main CLI entrypoint for OmniRAG-Ops."""
    parser = argparse.ArgumentParser(
        description="OmniRAG-Ops: Enterprise Multi-Tier Retrieval Engine CLI"
    )
    parser.add_argument(
        "--query", type=str, help="Search query string to process."
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=[
            "auto",
            "benchmark",
            "naive",
            "hybrid",
            "graph",
            "corrective",
            "agentic",
            "demo",
        ],
        help="Retrieval engine mode (default: auto router).",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="data/sample_corpus.json",
        help="Path to sample corpus JSON.",
    )

    args = parser.parse_args()

    if args.mode == "demo" or (not args.query and len(sys.argv) == 1):
        run_demo()
        return

    if not args.query:
        print_banner()
        print("Error: --query parameter required. Example:")
        print("  python main.py --query 'What is Raft?' --mode auto")
        sys.exit(1)

    corpus_path = args.corpus

    if args.mode == "auto":
        router = RAGRouter(corpus_path=corpus_path)
        output = router.route_and_execute(args.query)
        print(json.dumps(output, indent=2))

    elif args.mode == "benchmark":
        router = RAGRouter(corpus_path=corpus_path)
        output = router.benchmark_all_paradigms(args.query)
        print(json.dumps(output, indent=2))

    elif args.mode == "naive":
        engine = NaiveRAG(corpus_path=corpus_path)
        print(json.dumps(engine.generate(args.query), indent=2))

    elif args.mode == "hybrid":
        engine = HybridRAG(corpus_path=corpus_path)
        print(json.dumps(engine.generate(args.query), indent=2))

    elif args.mode == "graph":
        engine = GraphRAG(corpus_path=corpus_path)
        print(json.dumps(engine.generate(args.query), indent=2))

    elif args.mode == "corrective":
        engine = CorrectiveRAG(corpus_path=corpus_path)
        print(json.dumps(engine.generate(args.query), indent=2))

    elif args.mode == "agentic":
        engine = AgenticRAG(corpus_path=corpus_path)
        print(json.dumps(engine.run(args.query), indent=2))


if __name__ == "__main__":
    main()
