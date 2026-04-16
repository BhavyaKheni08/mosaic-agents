from enum import Enum

class NodeLabel(str, Enum):
    CLAIM = "CLAIM"
    ENTITY = "ENTITY"
    SOURCE = "SOURCE"
    AGENT = "AGENT"

class EdgeType(str, Enum):
    CONTRADICTS = "CONTRADICTS"
    SUPPORTS = "SUPPORTS"
    MADE_BY = "MADE_BY"
    MENTIONS = "MENTIONS"
    DERIVED_FROM = "DERIVED_FROM"
