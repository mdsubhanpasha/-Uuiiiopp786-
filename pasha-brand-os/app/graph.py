import os
from typing import Dict, Any, List, TypedDict, Optional
from loguru import logger

from langgraph.graph import StateGraph, END

from app.nodes.researcher import ResearcherNode
from app.nodes.ghostwriter import GhostwriterNode
from app.nodes.designer import DesignerNode
from app.nodes.critic import CriticNode

class GraphState(TypedDict, total=False):
    topic: str
    angle: str
    available_angles: List[Dict[str, Any]]
    source_urls: List[str]
    variants: Dict[str, str]
    selected_variant_type: str
    full_text: str
    hook: str
    problem: str
    insight: str
    cta: str
    hashtags: str
    image_prompts: List[str]
    selected_prompt: str
    image_url: str
    local_image_path: str
    virality_score: int
    hook_strength_score: int
    value_score: int
    authenticity_score: int
    cta_score: int
    predicted_views: str
    feedback: str
    passed: bool
    status: str
    retry_count: int

class BrandOSGraph:
    """
    Layer 2 Generation Engine - 4 Node LangGraph Workflow:
    - Node 1: Researcher (topic + angles + sources)
    - Node 2: Ghostwriter (3 variants using Qdrant style)
    - Node 3: Designer (DALL-E 3 image prompts & images)
    - Node 4: Critic & Virality Scorer (evaluates 0-100 score, loops back if score < 75)
    """

    def __init__(self):
        self.researcher = ResearcherNode()
        self.ghostwriter = GhostwriterNode()
        self.designer = DesignerNode()
        self.critic = CriticNode()
        self.workflow = self._build_graph()

    def _research_step(self, state: GraphState) -> GraphState:
        res = self.researcher.execute(dict(state))
        return {**state, **res}

    def _ghostwrite_step(self, state: GraphState) -> GraphState:
        res = self.ghostwriter.execute(dict(state))
        return {**state, **res}

    def _design_step(self, state: GraphState) -> GraphState:
        res = self.designer.execute(dict(state))
        return {**state, **res}

    def _critic_step(self, state: GraphState) -> GraphState:
        res = self.critic.execute(dict(state))
        retry = state.get("retry_count", 0) + 1
        return {**state, **res, "retry_count": retry}

    def _decide_next_node(self, state: GraphState) -> str:
        passed = state.get("passed", False)
        retry_count = state.get("retry_count", 0)

        if passed or retry_count >= 3:
            logger.info(f"Graph execution completing. Passed: {passed}, Retries: {retry_count}")
            return "end"
        else:
            logger.info(f"Virality score under 75. Retrying ghostwriting loop (Attempt {retry_count + 1}). Feedback: {state.get('feedback')}")
            return "ghostwriter"

    def _build_graph(self):
        builder = StateGraph(GraphState)

        builder.add_node("researcher", self._research_step)
        builder.add_node("ghostwriter", self._ghostwrite_step)
        builder.add_node("designer", self._design_step)
        builder.add_node("critic", self._critic_step)

        builder.set_entry_point("researcher")
        builder.add_edge("researcher", "ghostwriter")
        builder.add_edge("ghostwriter", "designer")
        builder.add_edge("designer", "critic")

        builder.add_conditional_edges(
            "critic",
            self._decide_next_node,
            {
                "ghostwriter": "ghostwriter",
                "end": END
            }
        )

        return builder.compile()

    def run(self, topic: Optional[str] = None, angle: Optional[str] = None) -> GraphState:
        initial_state: GraphState = {
            "topic": topic,
            "angle": angle,
            "retry_count": 0
        }
        return self.workflow.invoke(initial_state)
