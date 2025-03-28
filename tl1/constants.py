"""
Module used in the implementation:

- `enum`: Provides the `Enum` class, which serves as a base for creating enumeration types.
"""
from enum import Enum, auto

class StatusCode(Enum):
    """
        Status codes for TL1 response messages.
    
    Args:
        Enum (Enum): Generic Enumeration class
    """
    COMPLETED = 'COMPLD'
    DELAYED = 'DELAY'
    DENIED = 'DENY'
    PARTIALLY = 'PRTL'
    RETRIVED = 'RTRV'
    NONE = 'NONE'

class AlarmCode(Enum):
    """
    Alarm codes for TL1 response messages.

    Args:
        Enum (Enum): Base class for creating enumerations.
    """
    CRITIC = '*C'
    MAJOR = '**'
    MINOR = '*'
    WARN = 'A'

class Terminator(Enum):
    """
    TL1 response terminator characters.

    Args:
        Enum (Enum): Base class for creating enumerations.
    """
    CONTINUE = '>'
    STOP = ';'
    ACK = '<'

class ResponseType(Enum):
    """
    TL1 response Types

    ACK - Acknowledgement Message
    AUTO - Autonomous Message
    DEFAULT - Default Response format

    Args:
        Enum (Enum): Base class for creating enumerations.
    """
    ACK = auto()
    AUTO = auto()
    DEFAULT = auto()
