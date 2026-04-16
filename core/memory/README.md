# MOSAIC Memory Integration Guide

Welcome to Phase 1 of the MOSAIC GraphMemoryManager. This module handles knowledge as a graph, natively supporting and identifying contradictions between claims using Semantic Search (Qdrant) and LLM-based verification (Gemini).

## How to Connect New Modules

To use the memory system in a new file, simply import the `GraphMemoryManager` and instantiate it.

```python
from mosaic.core.memory.manager import GraphMemoryManager

memory = GraphMemoryManager()

# Example usage:
claim_id = memory.store_claim(
    content="The sky is red today.", 
    source_id="agent-xyz", 
    agent_id="agent-xyz"
)
```

## Open Entry Points (Hooks)

Below are the key entry points you can use to interact with the Memory System:

- **Input Hook**: `memory.store_claim(content, source_id, agent_id)`
  - Use this whenever an agent generates a statement. It automatically searches Qdrant for semantic collisions and uses an LLM to check for contradictions.
  
- **Inquiry Hook**: `memory.get_entity_graph(entity_name)`
  - Use this to pull everything known about a subject. Returns the entity node, associated claims, and other relationships.
  
- **Resolution Hook**: `memory.resolve_conflict(claim_id_a, claim_id_b, winner_id)`
  - Use this after a Debate/Phase 2 Agent completes resolving a contradiction to mark the winning claim.

- **Trigger Hook**: `memory.get_uncertain_nodes()`
  - Use this in Phase 2 agents to fetch all currently unresolved contradictions (claims connected by a `CONTRADICTS` edge) to trigger debates operations.

## Debugging & Logs

- **Stdout Logs**: All system logs are output to stdout with the prefix `[MOSAIC-MEMORY]`. This includes contradictions found and resolution notices.
- **Failures & Database Unavailability**: If Neo4j or Qdrant fails to connect, or if the LLM provider fails, operations are caught by a try-except block. The system will log a precise error (e.g. `[GraphMemoryManager.store_claim] Error: ...`) and dump the failed data payload into `fallback_storage.json`. 
- **Checking Fallbacks**: Always check `./fallback_storage.json` during debugging to verify if your claims were routed properly when the database is down.
