"""
Open Nodes & Extensibility:
Validator middleware is where new NLP fact-checkers, syntax guards, or schema evolution mechanisms
can be hooked into the protocol. Modifying validate_message allows the system to support new JSON variants.
"""
import json
import logging
from pydantic import ValidationError
from typing import Tuple

from core.debate.schema import DebateMessage
from core.debate.exceptions import SchemaMismatchError

logger = logging.getLogger("Validator")

def validate_message(raw_json: str, agent_id: str, debate_id: str) -> Tuple[DebateMessage, str]:
    """
    Attempts to parse a raw LLM string output into the strict DebateMessage Pydantic schema.
    Raises SchemaMismatchError on failure to enforce the schema boundary.
    """
    try:
        data = json.loads(raw_json)
        message = DebateMessage(**data)
        return message, ""
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON structure (JSONDecodeError): {str(e)}"
        # Traceability: Every validation failure is logged with the raw bad string
        logger.error(f"[Debate {debate_id}] Agent {agent_id} JSON Error: {raw_json}")
        raise SchemaMismatchError(error_msg, debate_id, agent_id, "json_parse")
    except ValidationError as e:
        error_msg = f"Pydantic Validation Error: {str(e)}"
        detailed_errors = e.errors()
        failed_field = detailed_errors[0]['loc'][0] if detailed_errors else "validation"
        # Traceability: Log exactly which field broke the schema mapping
        logger.error(f"[Debate {debate_id}] Agent {agent_id} Validation Error on field '{failed_field}': {raw_json}")
        raise SchemaMismatchError(error_msg, debate_id, agent_id, str(failed_field))

def get_correction_prompt(pydantic_error: str) -> str:
    """
    The auto-generated Correction Loop prompt sent back to hallucinative agents.
    """
    return (
        f"Your previous response failed validation. Error: {pydantic_error}. "
        "Please output ONLY the raw JSON object."
    )
