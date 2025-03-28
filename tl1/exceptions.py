"""
    Base class for custom exceptions in TL1-related operations.
"""

class TL1Exception(Exception):
    """
    Base class for all TL1-related exceptions.

    Inherits from the built-in `Exception` class to provide a custom exception
    for handling TL1-specific errors.
    """
    message = ''
    def __init__(self):
        super().__init__(self.message)

class PortRangeException(TL1Exception):
    """
    Exception raised when a port number is out of the valid range.

    This exception is specifically used when a port number is not between 0 and 65535,
    which are the valid bounds for port numbers in the TCP/IP protocol.
    """
    message = 'Port number must be between 0 and 65535'
    