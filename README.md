# AI Scenario Trainer

A multi-agent framework for scenario training involving Neo4j memory, debate protocols, and temporal decay auditing.

## Project Structure

- `core/`: Core logic and agent definitions.
  - `memory/`: Neo4j graph memory implementation.
  - `debate/`: Debate protocol and consensus logic.
  - `orchestrator/`: LLM routing and agent spawning.
  - `auditor/`: Temporal decay and memory auditing.
  - `agents/`: Individual agent specifications.
- `api/`: FastAPI backend with WebSockets support.
- `ui/`: React frontend for interaction and visualization.
- `benchmarks/`: Evaluation and testing scripts.
- `paper/`: Research documentation and LaTeX files.
- `docs/`: Technical documentation and schemas.

## Setup

1. Copy `.env.example` to `.env` and fill in necessary keys.
2. Run `make setup` to install dependencies.
3. Use `docker-compose up` to start infrastructure (Neo4j, Redis, etc.).
