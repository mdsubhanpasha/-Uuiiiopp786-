"""Graph RAG Engine implementation.

Uses NetworkX knowledge graphs for entity extraction, multi-hop relationship
traversal, and graph-augmented context synthesis.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Set

import networkx as nx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GraphRAG")


class GraphRAG:
    """Knowledge-graph multi-hop retrieval and context generation engine."""

    def __init__(self, corpus_path: Optional[str] = None) -> None:
        """Initialize GraphRAG instance.

        Args:
            corpus_path: Path to sample corpus JSON file.
        """
        self.graph = nx.DiGraph()
        self.documents: Dict[str, Dict[str, Any]] = {}

        if corpus_path and os.path.exists(corpus_path):
            self.load_corpus(corpus_path)

    def load_corpus(self, filepath: str) -> None:
        """Load corpus and construct NetworkX Knowledge Graph.

        Args:
            filepath: Path to corpus JSON file.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for doc in data:
            doc_id = doc["id"]
            self.documents[doc_id] = doc

            self.graph.add_node(
                doc_id, type="document", title=doc.get("title", "")
            )

            for entity in doc.get("entities", []):
                entity_id = f"entity:{entity.lower()}"
                self.graph.add_node(
                    entity_id, type="entity", name=entity
                )
                self.graph.add_edge(doc_id, entity_id, relation="MENTIONS")
                self.graph.add_edge(entity_id, doc_id, relation="CONTAINED_IN")

            for rel in doc.get("relations", []):
                src = f"entity:{rel['source'].lower()}"
                tgt = f"entity:{rel['target'].lower()}"
                rel_type = rel.get("relation", "RELATED_TO")

                self.graph.add_node(src, type="entity", name=rel["source"])
                self.graph.add_node(tgt, type="entity", name=rel["target"])
                self.graph.add_edge(src, tgt, relation=rel_type)

        logger.info(
            "GraphRAG initialized with %d nodes and %d edges.",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )

    def extract_entities_from_query(self, query: str) -> List[str]:
        """Identify matching entities present in query.

        Args:
            query: Input user query string.

        Returns:
            List of matching entity node IDs.
        """
        query_lower = query.lower()
        matched_entities: List[str] = []

        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "entity":
                entity_name = data.get("name", "").lower()
                if entity_name in query_lower or query_lower in entity_name:
                    matched_entities.append(node)

        return matched_entities

    def multi_hop_search(
        self, query: str, max_hops: int = 2
    ) -> Dict[str, Any]:
        """Perform multi-hop graph traversal starting from query entities.

        Args:
            query: Input user query.
            max_hops: Maximum graph traversal hops.

        Returns:
            Dict containing matched entities, subgraphs, and documents.
        """
        seed_entities = self.extract_entities_from_query(query)
        visited_nodes: Set[str] = set(seed_entities)
        current_frontier = set(seed_entities)

        traversed_edges: List[Dict[str, str]] = []
        doc_ids: Set[str] = set()

        for hop in range(max_hops):
            next_frontier: Set[str] = set()
            for node in current_frontier:
                if self.graph.nodes[node].get("type") == "document":
                    doc_ids.add(node)

                for neighbor in self.graph.successors(node):
                    edge_data = self.graph.get_edge_data(node, neighbor) or {}
                    traversed_edges.append({
                        "source": self.graph.nodes[node].get("name", node),
                        "relation": edge_data.get("relation", "CONNECTED"),
                        "target": self.graph.nodes[neighbor].get(
                            "name", neighbor
                        ),
                        "hop": str(hop + 1),
                    })
                    if neighbor not in visited_nodes:
                        visited_nodes.add(neighbor)
                        next_frontier.add(neighbor)

                for predecessor in self.graph.predecessors(node):
                    edge_data = (
                        self.graph.get_edge_data(predecessor, node) or {}
                    )
                    traversed_edges.append({
                        "source": self.graph.nodes[predecessor].get(
                            "name", predecessor
                        ),
                        "relation": edge_data.get("relation", "CONNECTED"),
                        "target": self.graph.nodes[node].get("name", node),
                        "hop": str(hop + 1),
                    })
                    if predecessor not in visited_nodes:
                        visited_nodes.add(predecessor)
                        next_frontier.add(predecessor)

            current_frontier = next_frontier

        for node in visited_nodes:
            if self.graph.nodes[node].get("type") == "document":
                doc_ids.add(node)

        retrieved_docs = [
            self.documents[doc_id]
            for doc_id in doc_ids
            if doc_id in self.documents
        ]

        return {
            "seed_entities": [
                self.graph.nodes[e].get("name", e) for e in seed_entities
            ],
            "traversed_relationships": traversed_edges[:10],
            "documents": retrieved_docs,
        }

    def generate(self, query: str, max_hops: int = 2) -> Dict[str, Any]:
        """Execute Graph RAG retrieval and multi-hop entity reasoning.

        Args:
            query: User query string.
            max_hops: Multi-hop graph depth.

        Returns:
            Dict containing Graph RAG response and graph metadata.
        """
        graph_results = self.multi_hop_search(query, max_hops=max_hops)
        entities = graph_results["seed_entities"]
        relations = graph_results["traversed_relationships"]
        docs = graph_results["documents"]

        rel_str = "\n".join(
            f"  - ({r['source']}) -[{r['relation']}]-> ({r['target']})"
            for r in relations
        ) or "  - No direct graph relationships found."

        doc_titles = ", ".join(d.get("title", "") for d in docs) or "None"

        response_text = (
            f"[Graph RAG Multi-Hop Response]\n"
            f"Identified Query Entities: {entities}\n"
            f"Traversed Knowledge Paths:\n{rel_str}\n\n"
            f"Connected Enterprise Documents: {doc_titles}\n"
            f"Synthesized Multi-Hop Conclusion for '{query}': Graph "
            f"traversal confirms structural connectivity."
        )

        return {
            "paradigm": "Graph RAG",
            "query": query,
            "seed_entities": entities,
            "traversed_relations": relations,
            "retrieved_documents": [
                {"id": d.get("id"), "title": d.get("title")} for d in docs
            ],
            "response": response_text,
        }
