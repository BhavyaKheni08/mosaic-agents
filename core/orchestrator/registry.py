import logging
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ModelTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ModelConfig(BaseModel):
    name: str = Field(..., description="Name of the model (e.g., gemini-1.5-flash)")
    tier: ModelTier = Field(..., description="Cost/Complexity tier")
    context_window: int = Field(default=8192, description="Max context length")

class AgentSpec(BaseModel):
    role: str = Field(..., description="Role of the dynamic agent")
    system_prompt: str = Field(..., description="System prompt defining behavior")
    tools: List[str] = Field(default_factory=list, description="Tool names available to agent")
    model_pref: ModelTier = Field(default=ModelTier.MEDIUM, description="Preferred model tier")

class CapabilityRegistry:
    """Registry to hold definitions of dynamic agents."""
    def __init__(self):
        self._agents: Dict[str, AgentSpec] = {}

    def register_agent(self, name: str, spec: AgentSpec) -> None:
        try:
            self._agents[name] = spec
            logger.info(f"[registry.py -> register_agent] | capabilities updated with: {name}")
        except Exception as e:
            logger.error(f"[registry.py -> register_agent] | Error: {e} | Context: {{'name': name, 'spec': spec}}")
            raise

    def get_agent(self, name: str) -> Optional[AgentSpec]:
        try:
            return self._agents.get(name)
        except Exception as e:
            logger.error(f"[registry.py -> get_agent] | Error: {e} | Context: {{'name': name}}")
            raise

class ModelRegistry:
    """Registry caching model selection configs mapping tiers to underlying identifiers."""
    def __init__(self):
        self._models: Dict[ModelTier, List[ModelConfig]] = {
            ModelTier.LOW: [],
            ModelTier.MEDIUM: [],
            ModelTier.HIGH: []
        }

    def register_model(self, config: ModelConfig) -> None:
        try:
            self._models[config.tier].append(config)
            logger.info(f"[registry.py -> register_model] | Model {config.name} added to tier {config.tier}.")
        except Exception as e:
            logger.error(f"[registry.py -> register_model] | Error: {e} | Context: {{'config': config}}")
            raise

    def get_model_for_tier(self, tier: ModelTier) -> Optional[ModelConfig]:
        try:
            models = self._models.get(tier, [])
            if not models:
                return None
            return models[0]  # Grab the primary active model for the tier
        except Exception as e:
            logger.error(f"[registry.py -> get_model_for_tier] | Error: {e} | Context: {{'tier': tier}}")
            raise
