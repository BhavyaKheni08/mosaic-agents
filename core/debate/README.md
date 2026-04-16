# MOSAIC Structured Debate Protocol

Welcome to the MOSAIC Structured Debate Protocol (`core/debate`), the engine of Phase 2 logic. This directory enforces a strict, JSON-schema-driven environment where agent disagreements are resolved predictably, averting open-ended conversational drift and hallucinations.

## Architecture & "Open Nodes"

This module is designed around an **"Open Nodes"** philosophy. Extensibility is baked into the component documentation (see the docstrings in each module). Developers can plug in new LLMs, custom validation guards, or graph database ingress/egress hooks seamlessly.

### Core Components

- **[`schema.py`](./schema.py)**: The strictly typed data definitions mapping `DebateMessage` and `DebateSession` forms (via Pydantic). It dictates constraints such as composite confidence parameters and exact message types (`CLAIM`, `CHALLENGE`, `EVIDENCE`, `REBUTTAL`, etc.).
- **[`validator.py`](./validator.py)**: Validation Middleware. Intercepts raw LLM outputs and strictly enforces Pydantic boundaries. It captures corrupt JSON fragments for telemetry and triggers recursive format-correction prompts if agents hallucinate formatting.
- **[`engine.py`](./engine.py)**: The strict, asynchronous state machine. It handles:
  - Round limits and concurrency limits.
  - State Transition guards (e.g., stopping an agent from escalating directly after a normal claim).
  - Logical inconsistency detections (e.g., rejecting an agent displaying absolute confidence when it provides zero graph references).
- **[`registry.py`](./registry.py)**: The Integration Hub. Manages model routing mappings (hooking specific system prompts explicitly to `gpt-4o` vs `claude-3-5-sonnet`), tracks locked nodes across active debates, and defines standard orchestrator escalation pathways.
- **[`agents.py`](./agents.py)**: System prompt and behavior abstractions framing the generic Researcher, Critic, and Synthesizer endpoints inheriting from `registry.py`.
- **[`exceptions.py`](./exceptions.py)**: A detailed fallback taxonomy (such as `DebateTimeoutError` and `SchemaMismatchError`). Every exception implements a unified `diagnostic_hint` to simplify traceback debugging.

## How the Protocol Works

1. **Initialization:** A conflict spawns a `DebateSession`. Graph indices being analyzed are conceptually "locked" in the `registry.py` connections mapping.
2. **Discourse:** The Researcher and Critic iterate synchronously through predefined states.
3. **The Validation Gate:** Every agent action routes strictly through `validator.py`. Valid `DebateMessage` payloads advance into the timeline; faulty objects queue a Format Correction prompt iteratively repeating up to a configured threshold.
4. **Resolution:** The loop concludes via explicit CONCEDE triggers, or hits a threshold cap triggering an ESCALATE protocol out to the human-in-the-loop orchestrator hook.
5. **Egress:** Final synthesized determinations are committed back into Vector/Graph stores via the registry's explicit data hooks.
