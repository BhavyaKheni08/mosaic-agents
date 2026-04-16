# Graph Schema

The Neo4j memory uses the following schema:

## Nodes

- `Agent`: Represents an AI agent.
- `Event`: Represents a simulation event.
- `Fact`: Represents a piece of knowledge.

## Relationships

- `(Agent)-[:KNOWS]->(Fact)`
- `(Event)-[:INVOLVES]->(Agent)`
- `(Fact)-[:DECAYED_AT]->(Timestamp)`
