from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

def generate_uuid() -> str:
    return str(uuid4())

class Claim(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    content: str
    source_id: str
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Entity(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    type: str

class Source(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    type: str
    url_or_path: str

class AgentSession(BaseModel):
    session_id: str = Field(default_factory=generate_uuid)
    agent_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)

class DebateSession(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    claim_a_id: str
    claim_b_id: str
    status: str = "PENDING"  # PENDING, RESOLVED
    winner_id: Optional[str] = None
