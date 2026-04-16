from typing import Callable, Dict, Optional, Any

class Connector:
    """
    The Open Node registry for the CLI.
    Maps Capabilities to Functions so new files can 'plug in' seamlessly.
    """
    def __init__(self):
        self._registry: Dict[str, Callable] = {}
        self._modules: Dict[str, str] = {}

    def link_new_module(self, name: str, path: str):
        """
        Connects a new module or agent to the existing CLI flow.
        
        Usage:
            registry.link_new_module("debate_agent", "cli.agents.debate")
        """
        self._modules[name] = path

    def register_command(self, capability: str):
        """
        Decorator to register a CLI command or capability to an 'Open Node'.
        """
        def decorator(func: Callable):
            self._registry[capability] = func
            return func
        return decorator

    def get_capability(self, capability: str) -> Optional[Callable]:
        """
        Retrieves a registered function for a given capability.
        """
        return self._registry.get(capability)

    @property
    def registered_modules(self) -> Dict[str, str]:
        """Returns all linked modules."""
        return self._modules

    @property
    def available_capabilities(self) -> list[str]:
        """Returns a list of all registered command capabilities."""
        return list(self._registry.keys())
        
# Global registry acting as the single source of truth for CLI Hooks
registry = Connector()
