# 🏛 MOSAIC System Architecture

## 🌐 Holistic Overview
MOSAIC is built on a **Decoupled Agentic Architecture**. Unlike monolithic AI systems, MOSAIC separates *reasoning*, *memory*, and *validation* into distinct, interacting services. This allow for high observability and precision control over the cognitive state of the system.

## 🏗 Modular Layers

### 1. **Cognitive Orchestration (LangGraph VM)**
The orchestrator acts as the "Prefrontal Cortex" of the system.
- **State Management:** Uses a global state object passed between nodes.
- **Node Execution:** Each node is a specialized agent or a tool call.
- **Dynamic Routing:** Conditional edges determine the flow based on agent outputs or confidence thresholds.

### 2. **Multi-Modal Memory (Neo4j + Qdrant)**
The dual-database strategy ensures both structural and semantic coherence.
- **Neo4j:** Stores entities, relationships, and **contradiction nodes**. It forms the "Relational Memory."
- **Qdrant:** Stores vector embeddings of claims for "Associative Awareness," enabling fast retrieval of contextually relevant snippets.

### 3. **The Dialectical Core (Debate Protocol)**
To ensure high-fidelity knowledge, MOSAIC implements a **Structured Debate Engine**.
- **Thesis/Antithesis/Synthesis:** Agents are assigned roles to argue for and against new claims.
- **Consensus Scoring:** A cross-agent scoring mechanism determines if a claim is merged into the master graph or placed in a "Limbo" state for further auditing.

### 4. **Entropy Management (Temporal Auditor)**
Information has a half-life. The Auditor implements a **Decay Function**:
$$Confidence_{now} = Confidence_{initial} \times e^{-\lambda t}$$
Where $\lambda$ varies by node type (e.g., "Scientific Fact" decays slower than "Current Event").

---

## 🔄 Lifecycle of a Claim

1.  **Ingestion:** Agent extracts a claim from a source.
2.  **Vector Check:** Qdrant checks for semantically similar existing claims.
3.  **Graph Check:** Neo4j checks for structural contradictions (e.g., Agent A says X, Agent B previously said NOT X).
4.  **Debate:** If a conflict is found, the Debate Engine is triggered.
5.  **Audit:** Periodic sweeps by the Auditor re-validate confidence scores of all nodes.

---

## 🛠 Scalability & Integration
MOSAIC is built to be **Model Agnostic**. The services communicate via a standardized **Event Bus**, allowing for:
- Swapping LLM providers (Google Gemini, OpenAI, Anthropic).
- Plugging in specialized local models (Llama-3, Mistral) for auditing tasks.
- Real-time monitoring via the `api` WebSocket stream.
