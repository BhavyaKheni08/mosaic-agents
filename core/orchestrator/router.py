import logging
from typing import Optional
from .registry import ModelTier, ModelRegistry, ModelConfig

logger = logging.getLogger(__name__)

class TaskClassifier:
    """Classifies user queries to determine the required domain and complexity."""
    def __init__(self):
        pass

    def classify_query(self, query: str) -> ModelTier:
        try:
            # Basic stub classification logic based on query properties
            tier = ModelTier.LOW
            if len(query) > 500 or "analyze" in query.lower() or "complex" in query.lower():
                tier = ModelTier.HIGH
            elif len(query) > 100 or "summarize" in query.lower():
                tier = ModelTier.MEDIUM
            
            logger.info(f"[router.py -> classify_query] | Reasoning: Classification: {tier.value} based on query properties.")
            return tier
        except Exception as e:
            logger.error(f"[router.py -> classify_query] | Error: {e} | Context: {{'query': query[:50]}}")
            # Fallback to highest reasoning tier on classifier failure
            return ModelTier.HIGH

class ModelRouter:
    """Selects the correct LLM based on task classification and current model registry."""
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def route(self, query: str, explicit_tier: Optional[ModelTier] = None) -> ModelConfig:
        try:
            # Honor explicit tier requests, otherwise classify dynamically
            if explicit_tier:
                tier = explicit_tier
                logger.info(f"[router.py -> route] | Reasoning: Routing to explicit tier {tier.value}")
            else:
                classifier = TaskClassifier()
                tier = classifier.classify_query(query)
                logger.info(f"[router.py -> route] | Reasoning: Routing based on TaskClassifier to tier {tier.value}")
            
            model_config = self.registry.get_model_for_tier(tier)
            if not model_config:
                raise ValueError(f"No model registered for tier {tier.value}")
                
            return model_config
            
        except Exception as e:
            logger.error(f"[router.py -> route] | Error: {e} | Context: {{'query': query[:50], 'explicit_tier': explicit_tier}}")
            # Raise exception so the orchestrator node can failover to the RecoveryNode
            raise
