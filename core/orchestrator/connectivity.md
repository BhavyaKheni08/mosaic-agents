# Phase 3 Orchestrator: Connectivity & Extensibility Blueprint

This document outlines the design principles for connecting new capabilities and states into the dynamic LangGraph orchestrator. The core orchestrator uses an "Open Nodes" and "Open State" pattern to avoid breaking core routines when expanding functionalities.

## Open State Blueprint

The central data structure passed between nodes in the LangGraph Orchestrator is `OrchestratorState`, defining standard fields alongside extensibility hooks.

```python
class OrchestratorState(TypedDict):
    # Standard Routing Interfaces
    query: str
    result: Optional[str]
    error: Optional[str]
    messages: Annotated[list, operator.add]
    
    # Internal orchestration properties
    required_role: Optional[str]
    target_tier: Optional[ModelTier]
    current_agent: Optional[AgentSpec]
    model_config: Optional[ModelConfig]

    # Open Hooks
    metadata: Dict[str, Any]
    custom_context: Dict[str, Any]
```

### State Extension Rules
1.  **Avoid top-level fields**: Do not add new top-level specific fields for transient features or single-agent data.
2.  **`custom_context`**: If a routing module (e.g., preprocessing tools from Phase 2) needs to relay specific information directly to the `specialist_node` prompt without injecting into general chat history, insert that data inside `custom_context`.
3.  **`metadata`**: Utilize this dictionary to monitor execution states, log telemetry, or set flags useful for downstream pipeline components.

## Open Node Strategy

Nodes remain decoupled from precise system prompts or direct LangChain instances.

*   `orchestrator_node`: Exists solely to parse `CapabilityRegistry` representations based on query classifications and route the data.
*   `specialist_node`: Functions as a pure "slot". It does not know what it executes; it offloads the mapping to the `AgentLifecycleManager` provided by the graph components.
*   `recovery_node`: Functions as a failover domain decoupled from explicit business logic, solely focused on extracting readable constraints from errors.

### Hooking in New Components

1.  **Construct Spec**: Describe what the dynamic agent should do via the Pydantic schemas.
    ```python
    spec = AgentSpec(
        role="bio_analyst", 
        system_prompt="You are a sequence processing specialist. Identify the target properties.",
        tools=["process_seq_tool"],
        model_pref=ModelTier.HIGH
    )
    ```
2.  **Register Node Capability**: Inject into the `CapabilityRegistry`.
    ```python
    capabilities.register_agent("bio_analyst", spec)
    ```
3.  **Run Graph Invocation**: Trigger the master engine passing in the base config, specifically focusing the `required_role`.

## External Tool Connectivity

Currently, the `AgentLifecycleManager` uses simple mocks for tool resolution (`resolve_tools()`) to decouple orchestrator compilation from tool implementation. 

For future integrations:
*   Pass necessary tools strictly as text definitions within `AgentSpec.tools` arrays.
*   Later phases should overhaul the `AgentLifecycleManager.resolve_tools()` function so that it queries a global tool dictionary (binding `@tool` decorators) mapping the text strings into initialized `BaseTool` objects before they stream into the LangGraph React agent creation.
