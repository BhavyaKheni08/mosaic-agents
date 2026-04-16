"""
Open Nodes & Extensibility:
The DebateEngine's asynchronous state machine defines the debate control flow. Additional transition rules
can be added here to govern more complex multi-agent topologies (e.g., a "Moderator" agent stepping in).
"""
import logging
import asyncio
from typing import Callable, Optional, Awaitable

from core.debate.schema import DebateSession, DebateMessage, MessageType, SessionStatus
from core.debate.exceptions import (
    LogicalInconsistencyError, DebateTimeoutError
)
from core.debate.validator import validate_message, get_correction_prompt

class DebateEngine:
    """
    Asynchronous strict state machine that manages the flow and transitions of a Debate.
    """
    def __init__(self, session: DebateSession, max_retries: int = 2, timeout_sec: float = 30.0):
        self.session = session
        self.max_retries = max_retries
        self.timeout_sec = timeout_sec
        self.logger = self._setup_logger()
        self._step_sequence = 0

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"DebateEngine_{self.session.debate_id}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s | [%(levelname)s] | DebateID: %(debate_id)s | AgentID: %(agent_id)s | Step: %(step_sequence)s | %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _log(self, level: int, message: str, agent_id: str):
        extra = {
            'debate_id': self.session.debate_id,
            'agent_id': agent_id,
            'step_sequence': self._step_sequence
        }
        self.logger.log(level, message, extra=extra)

    def _flag_resolution(self, resolution_type: str):
        """Update session status depending on how the loop ends."""
        if resolution_type == "CONCEDE":
            self.session.status = SessionStatus.RESOLVED
            self.session.active = False
            self._log(logging.INFO, "Debate formally marked RESOLVED via CONCEDE.", "ENGINE")
        elif resolution_type in ["ESCALATE", "MAX_ROUNDS"]:
            self.session.status = SessionStatus.UNRESOLVED_FOR_HUMAN_REVIEW
            self.session.active = False
            self._log(logging.WARNING, f"Debate escalated ({resolution_type}), marked UNRESOLVED_FOR_HUMAN_REVIEW.", "ENGINE")
            
            # Orchestrator Integration Hook
            from core.debate.registry import escalate_to_orchestrator
            # Stores the full transcript as a node or pushes to human orchestrator
            escalate_to_orchestrator(self.session)

    def _validate_transition(self, current_message_type: MessageType):
        """
        Enforce strict state transition rules to prevent freeform conversations.
        """
        if not self.session.messages:
            return  # Genesis message, no prior state to check
            
        last_message = self.session.messages[-1]
        
        if last_message.message_type == MessageType.CLAIM:
            if current_message_type not in [MessageType.CHALLENGE, MessageType.EVIDENCE]:
                raise LogicalInconsistencyError(
                    f"Invalid Transition: After a CLAIM, move must be CHALLENGE or EVIDENCE. Got {current_message_type.value}.",
                    self.session.debate_id, "ENGINE", "message_type"
                )
        elif last_message.message_type == MessageType.CHALLENGE:
            if current_message_type not in [MessageType.REBUTTAL, MessageType.CONCEDE, MessageType.ESCALATE]:
                raise LogicalInconsistencyError(
                    f"Invalid Transition: After a CHALLENGE, move must be REBUTTAL, CONCEDE, or ESCALATE. Got {current_message_type.value}.",
                    self.session.debate_id, "ENGINE", "message_type"
                )

    async def execute_agent(self, agent_id: str, agent_coro: Callable[[Optional[str]], Awaitable[str]]) -> DebateMessage:
        """
        Async execution wrapper featuring Validation Middleware, Correction Loop, and Timeouts.
        """
        self._step_sequence += 1
        retry_count = 0
        error_hint = None

        while retry_count <= self.max_retries:
            self._log(logging.INFO, f"Executing async agent {agent_id} (Attempt {retry_count + 1})", agent_id)
            try:
                # We enforce an asynchronous timeout constraint to prevent hang execution
                raw_response = await asyncio.wait_for(agent_coro(error_hint), timeout=self.timeout_sec)
                
                # Validation Middleware Gate
                message, _ = validate_message(raw_response, agent_id, self.session.debate_id)
                self._log(logging.INFO, f"Validation successful. Computed Type: {message.message_type.value}", agent_id)
                return message
                
            except SchemaMismatchError as e:
                self._log(logging.WARNING, f"Validation failed. {e.diagnostic_hint}", agent_id)
                error_hint = get_correction_prompt(str(e))
                retry_count += 1
            except asyncio.TimeoutError:
                err = DebateTimeoutError("Agent connection or processing timed out.", self.session.debate_id, agent_id, "timeout")
                self._log(logging.ERROR, "DebateTimeoutError triggered.", agent_id)
                raise err
                
        self._log(logging.ERROR, "Max format retries exceeded.", agent_id)
        # Automatic timeout/fail escalation
        self._flag_resolution("ESCALATE")
        return DebateMessage(
            debate_id=self.session.debate_id, 
            agent_id="SYSTEM", 
            message_type=MessageType.ESCALATE, 
            content="FormatRetry correction loop completely exhausted."
        )

    async def process_message(self, message: DebateMessage):
        """Append message to session and evaluate transition, logical consistency rules."""
        
        # 1. State Transition Rule Adherence
        try:
            self._validate_transition(message.message_type)
        except LogicalInconsistencyError as e:
            self._log(logging.ERROR, str(e), message.agent_id)
            self._flag_resolution("ESCALATE")
            raise e

        # 2. Record Message
        self.session.messages.append(message)
        
        # 3. High-Confidence Evidence Check
        if message.composite_confidence is not None and message.composite_confidence >= 0.8:
            if not message.references:
                raise LogicalInconsistencyError(
                    "LogicalInconsistencyError: Agent reported high confidence (>0.8) without verifying graph references.",
                    self.session.debate_id, message.agent_id, "references"
                )

        # 4. End Condition Logic
        if message.message_type == MessageType.CONCEDE:
            self._flag_resolution("CONCEDE")
        elif message.message_type == MessageType.ESCALATE:
            self._flag_resolution("ESCALATE")

    async def step_round(self) -> bool:
        """Round Manager. Returns False if debate formally concludes via limit."""
        self._step_sequence += 1
        
        if self.session.current_round >= self.session.max_rounds:
            self._log(logging.WARNING, f"Max rounds ({self.session.max_rounds}) hit. Flagging UNRESOLVED_FOR_HUMAN_REVIEW.", "ENGINE")
            self._flag_resolution("MAX_ROUNDS")
            return False
            
        self.session.current_round += 1
        self._log(logging.INFO, f"Advanced to round {self.session.current_round}", "ENGINE")
        return True
