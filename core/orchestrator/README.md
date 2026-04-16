# Phase 3 Orchestrator

The Phase 3 Orchestrator is the central nervous system of the MOSAIC project, built upon a "Virtual Machine" architecture using LangGraph. This component employs a **Dynamic Agent Slot** pattern, where a singular capability-agnostic graph dynamically mounts and unmounts specialized agent configurations depending on the task's classified complexity and required role.

## 🏗 Directory Architecture

This module is designed for strict robustness, fault tolerance, and extensibility.

*   `registry.py` - Contains the foundational Pydantic schemas (`AgentSpec`, `ModelConfig`, `ModelTier`) and the runtime registry stores (`CapabilityRegistry`, `ModelRegistry`) that track available resources.
*   `router.py` - Implements the `TaskClassifier` (for evaluating query scope/complexity) and the `ModelRouter` (to match the query with the optimal cost/performance model tier).
*   `engine.py` - Defines the `OrchestratorState` explicitly typed dictionary. Contains the core compiled `StateGraph` node logic (`orchestrator_node`, `specialist_node`, `recovery_node`) and conditional failover pathways.
*   `lifecycle.py` - Houses the `AgentLifecycleManager` that bridges the abstract `AgentSpec` into an active LangGraph `create_react_agent` executor, resolving dependencies and dissolving runtime contexts.
*   `connectivity.md` - Technical blueprint outlining how external modules hook into the ecosystem utilizing the 'Open Node' structures without hard-refactoring the core.

## ⚙️ Core Philosophies

1. **Robust Error Handling**: Every action operates within strictly trapped execution contexts. Rather than cascading thread crashes, systematic execution faults immediately route out via conditional edges (such as to the `recovery_node`) pushing normalized, diagnostic responses up to the user layout.
2. **Open Extensibility**: The underlying graph state isolates routing telemetry into generic dictionaries (`custom_context`, `metadata`). New preprocessing tools or analysis steps introduced in future phases can simply funnel data directly into these open slots without modifying `engine.py`.
3. **Traceability**: All decisions—from the classifier's routing deductions to the lifecycle spawn hooks mapping onto tool strings—are systematically logged utilizing standard module logging protocols ensuring transparent reasoning.

## 🚀 Usage 

The `build_orchestrator_engine()` (found in `engine.py`) requires prepopulated `CapabilityRegistry` and `ModelRegistry` models.

```python
# 1. Initialize Registries
capabilities = CapabilityRegistry()
models = ModelRegistry()

# 2. Register Active LLMs and Capabilities
models.register_model(ModelConfig(name="gemini-1.5-pro", tier=ModelTier.MEDIUM))
capabilities.register_agent("data_analyst", AgentSpec(role="...", system_prompt="..."))

# 3. Compile Graph Engine
app = build_orchestrator_engine(capabilities, models)

# 4. Invoke the Flow
final_state = app.invoke({"query": "Analyze these files...", "required_role": "data_analyst"})
```
