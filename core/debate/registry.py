"""
Open Nodes & Extensibility (The Manual for the Future):
This module defines the ingress and egress points of the Graph. 
- Graph Ingress occurs implicitly when Researchers/Critics analyze existing nodes to construct Claims.
- Graph Egress occurs explicitly within hook_into_graph() by the Synthesizer.
- New agents, models mapping, and coordination routines must be registered here.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.debate.schema import DebateSession

# CONNECTIONS dictionary tracks which Graph IDs are currently "locked" by an active debate.
CONNECTIONS: Dict[str, str] = {}

# Model Agnostic Mapping to handle heterogeneous debates.
MODEL_ROUTING_MAP: Dict[str, str] = {
    "Researcher_01": "gpt-4o",
    "Critic_01": "claude-3-5-sonnet-20240620",
    "Synthesizer_01": "gemini-1.5-pro",
}

class BaseDebateParticipant(ABC):
    """
    Abstract base class for all agents or graph-connectors that hook into the debate loop.
    """
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Automatically look up LLM config based on heterogeneous mapping
        self.model_config = MODEL_ROUTING_MAP.get(self.agent_id, "default-model")

    @abstractmethod
    def generate_response(self, error_hint: Optional[str] = None, context: Optional[str] = None) -> str:
        """Core generation method that must yield a pure JSON string block."""
        pass

def hook_into_graph(debate_id: str, final_claim_node: Dict[str, Any]) -> bool:
    """
    Graph Egress Point.
    Where the Synthesizer writes the final SynthesizedClaim node back to the global state.
    """
    node_id = final_claim_node.get("node_id")
    # Steps for external contributors:
    # 1. Update the structured Neo4j graph using GraphMemoryManager
    # 2. Resync the Qdrant vector store with updated embeddings
    
    # Unlock connection mapping once saved
    if node_id in CONNECTIONS and CONNECTIONS[node_id] == debate_id:
        del CONNECTIONS[node_id]
        
    return True

def escalate_to_orchestrator(session: DebateSession):
    """
    Orchestrator Hook. 
    Passed the entire DebateSession object when agents hit a stalemate, max rounds, or fatal system failure.
    """
    # Developers can link this to a Human-in-the-Loop dispatch queue,
    # a top-level Supervisor, or direct it to a dead-letter diagnostic node.
    pass
