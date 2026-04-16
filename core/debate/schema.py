"""
Open Nodes & Extensibility:
This Schema module tightly defines the data interchange format of the debate. To support new multi-modal or external-action 
capabilities, developers can extend the fields of DebateMessage here.
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone

class MessageType(str, Enum):
    CLAIM = "CLAIM"
    EVIDENCE = "EVIDENCE"
    CHALLENGE = "CHALLENGE"
    REBUTTAL = "REBUTTAL"
    CONCEDE = "CONCEDE"
    ESCALATE = "ESCALATE"

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    UNRESOLVED_FOR_HUMAN_REVIEW = "UNRESOLVED_FOR_HUMAN_REVIEW"

class DebateMessage(BaseModel):
    """
    Core schema for any message passed between agents in the Phase 2 Structured Debate Protocol.
    """
    message_id: str = Field(..., description="Unique identifier for this specific message.")
    debate_id: str = Field(..., description="Unique identifier for the active debate session.")
    agent_id: str = Field(..., description="The ID of the message author.")
    model_used: str = Field(..., description="The exact underlying model string (e.g., gpt-4o).")
    message_type: MessageType = Field(..., description="The structured class/type of the message.")
    content: str = Field(..., description="The primary payload, explanation, or text of the message.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="How certain the agent is (0.0 to 1.0).")
    references: List[str] = Field(
        default_factory=list, 
        description="IDs or URIs of external graph nodes, evidence items, or prior claims being referenced."
    )
    composite_confidence: Optional[float] = Field(
        default=None, 
        ge=0.0, le=1.0, 
        description="Composite Confidence Score (typically computed by Synthesizer)."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional telemetry or additional structured attributes."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Time the message was generated."
    )

class DebateSession(BaseModel):
    """
    State representation of an ongoing debate between agents.
    """
    debate_id: str = Field(..., description="Unique identifier for the debate session.")
    topic: str = Field(..., description="The central issue, node-conflict, or theme being debated.")
    messages: List[DebateMessage] = Field(default_factory=list, description="Ordered history of all debate messages.")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Current resolution state of the session.")
    active: bool = Field(default=True, description="Whether the debate is currently open/running.")
    current_round: int = Field(default=1, description="Round counter, managed by the state machine engine.")
    max_rounds: int = Field(default=3, description="Threshold limit before forced escalation and termination.")
