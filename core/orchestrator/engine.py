import logging
import operator
from typing import Annotated, Any, Dict, Optional, TypedDict

# Import logic with fallbacks
try:
    from langgraph.graph import StateGraph, START, END
except ImportError:
    # Stand-in for decoupled tests
    START = "__start__"
    END = "__end__"
    StateGraph = Any

from .registry import CapabilityRegistry, ModelRegistry, AgentSpec, ModelConfig, ModelTier
from .router import ModelRouter
from .lifecycle import AgentLifecycleManager

logger = logging.getLogger(__name__)

# --- Graph State Definition ---
class OrchestratorState(TypedDict):
    """The 'Open' State blueprint for the Orchestrator graph."""
    query: str
    result: Optional[str]
    error: Optional[str]
    
    # Internal orchestrator context
    required_role: Optional[str]
    target_tier: Optional[ModelTier]
    current_agent: Optional[AgentSpec]
    model_config: Optional[ModelConfig]
    
    # "Open Node" extensibility hooks
    metadata: Dict[str, Any]
    custom_context: Dict[str, Any]
    
    # Message reducer stream for LLMs
    messages: Annotated[list, operator.add]

# --- Node Implementations ---
def orchestrator_node(state: OrchestratorState, registries: Dict[str, Any]) -> dict:
    """Analyzes the query and prepares the AgentSpec via classification."""
    try:
        query = state.get("query", "")
        # role defaults for testing if missing
        role = state.get("required_role") or "default_specialist"
        
        cap_reg: CapabilityRegistry = registries["capabilities"]
        mod_reg: ModelRegistry = registries["models"]
        
        agent_spec = cap_reg.get_agent(role)
        if not agent_spec:
            raise ValueError(f"Agent role '{role}' not found in CapabilityRegistry.")
            
        router = ModelRouter(mod_reg)
        model_config = router.route(query, explicit_tier=state.get("target_tier"))
        
        logger.info(f"[engine.py -> orchestrator_node] | Assigned role: {role}, model: {model_config.name}")
        
        return {
            "current_agent": agent_spec,
            "model_config": model_config,
            "metadata": {"orchestrator_processed": True}
        }
    except Exception as e:
        logger.error(f"[engine.py -> orchestrator_node] | Error: {e} | Context: {{'keys': list(state.keys())}}")
        return {"error": str(e)}

def specialist_node(state: OrchestratorState) -> dict:
    """The Dynamic Agent Slot executing the loaded specification."""
    agent_spec = state.get("current_agent")
    model_config = state.get("model_config")
    
    if not agent_spec or not model_config:
        logger.error(f"[engine.py -> specialist_node] | Error: Missing agent spec or model config | Context: {{'has_spec': bool(agent_spec), 'has_model': bool(model_config)}}")
        return {"error": "Missing components for specialist slot."}

    lifecycle = AgentLifecycleManager()
    agent_instance = None
    try:
        agent_instance = lifecycle.spawn_agent(agent_spec, model_config)
        
        # Simulate agent execution for Phase 3 mock
        result = f"Execution from '{agent_spec.role}' complete using {model_config.name}."
        
        return {
            "result": result,
            "messages": [{"role": "assistant", "content": result}]
        }
    except Exception as e:
        logger.error(f"[engine.py -> specialist_node] | Error: {e} | Context: {{'spec_role': getattr(agent_spec, 'role', 'Unknown')}}")
        return {"error": str(e)}
    finally:
        if agent_instance:
            lifecycle.dissolve_agent(agent_instance)

def recovery_node(state: OrchestratorState) -> dict:
    """Diagnostic node handling fallbacks and bubbling human-readable errors."""
    error_msg = state.get("error", "Unknown error")
    query = state.get("query", "")
    
    logger.info(f"[engine.py -> recovery_node] | Evaluating failure state for query: {query[:30]}")
    try:
        # In real ops, a HIGH tier LLM processes error_msg here.
        diagnostic = f"Diagnostic Recovery: Action failed with internal error '{error_msg}'."
        
        return {
            "result": diagnostic,
            "messages": [{"role": "assistant", "content": diagnostic}],
            "error": None
        }
    except Exception as e:
        logger.error(f"[engine.py -> recovery_node] | Error: {e} | Context: {{'underlying_error': error_msg}}")
        return {"result": f"Systematic multi-level failure: {e}"}

# --- Edge Logic ---
def route_orchestrator(state: OrchestratorState) -> str:
    if state.get("error"):
        return "recovery"
    return "specialist"

def route_specialist(state: OrchestratorState) -> str:
    if state.get("error"):
        return "recovery"
    return END

# --- Graph Assembly Engine ---
def build_orchestrator_engine(capabilities: CapabilityRegistry, models: ModelRegistry):
    if StateGraph is Any:
        # Avoid compiling if langgraph absent
        return None
        
    try:
        builder = StateGraph(OrchestratorState)
        
        builder.add_node("orchestrator", lambda state: orchestrator_node(state, {"capabilities": capabilities, "models": models}))
        builder.add_node("specialist", specialist_node)
        builder.add_node("recovery", recovery_node)

        builder.add_edge(START, "orchestrator")
        
        builder.add_conditional_edges(
            "orchestrator",
            route_orchestrator,
            {"specialist": "specialist", "recovery": "recovery"}
        )
        
        builder.add_conditional_edges(
            "specialist",
            route_specialist,
            {END: END, "recovery": "recovery"}
        )
        
        builder.add_edge("recovery", END)
        
        return builder.compile()
    
    except Exception as e:
        logger.error(f"[engine.py -> build_orchestrator_engine] | Error: {e} | Context: {{'building_graph': True}}")
        raise
