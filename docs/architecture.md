# Architecture Overview

## System Components

1.  **Core Framework**: Orchestrates agents and manages state.
2.  **Memory (Neo4j)**: Persistent graph database for long-term relational memory.
3.  **Debate Protocol**: Multi-agent consensus mechanism.
4.  **Auditor**: Handles temporal decay and information validation.

## Data Flow

- User requests are routed via the Orchestrator.
- Agents interact with Memory and perform Debate.
- Auditor periodically reviews Memory for decay.
