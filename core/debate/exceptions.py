"""
Open Nodes & Extensibility:
This Exceptions module forms the basis for error-handling across the Structured Debate Protocol.
As the engine scales, developers can add new exception classes here to define "Fallback" identities 
for specific agent hallucination patterns or graph ingestion blockers.
"""
class DebateError(Exception):
    """Base exception for the debate lifecycle."""
    def __init__(self, message: str, debate_id: str = "unknown", agent_id: str = "unknown", failed_field: str = "unknown"):
        super().__init__(message)
        self.debate_id = debate_id
        self.agent_id = agent_id
        self.failed_field = failed_field

    @property
    def diagnostic_hint(self) -> str:
        """Traceback Meta: Diagnostic Hint indicating which agent failed and specific field issue."""
        return f"Diagnostic Hint: Agent '{self.agent_id}' failed on field '{self.failed_field}' during debate '{self.debate_id}'."

class InvalidSchemaError(DebateError):
    """Raised when an agent provides an invalid JSON schema."""
    pass

class SchemaMismatchError(DebateError):
    """Raised when validation middleware fails to parse the LLM output into the schema."""
    pass

class MaxRoundsExceeded(DebateError):
    """Raised when the debate exceeds the maximum allowed rounds."""
    pass

class ReferenceNotFoundError(DebateError):
    """Raised when a referenced evidence or claim is not found in the graph or session."""
    pass

class DebateTimeoutError(DebateError):
    """Raised when the asynchronous loop hangs and an agent operation times out."""
    pass

class EvidenceContradictionError(DebateError):
    """Raised when a Critic finds a direct conflict or explicit contradiction in the Graph."""
    pass

class LogicalInconsistencyError(DebateError):
    """Raised when an agent's confidence score is high but its references are empty."""
    pass
