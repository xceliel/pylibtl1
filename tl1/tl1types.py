"""
Imports required for the implementation:

- `TypeVar`, `Optional`, `Union` from `typing`: Used for type hinting and defining flexible types.
- `ipaddress`: Provides capabilities for working with and manipulating IP addresses.
- `PortRangeException` from `exceptions`: Exception raised when a port number is out of valid range.
"""

from typing import (
    TypeVar,
    Union
)

import ipaddress
from .exceptions import PortRangeException


#Generic data type
T = TypeVar('T')

class NumberBooleanMixin:
    """
    A mixin class to represent both Boolean and numeric values.

    In TL1, both Boolean and numeric values are represented as numbers.
    This class facilitates handling of such mixed data types.
    """

    __slots__ = ('value',)

    def __init__(self, value:T = False):
        """
            Receives a value, any value being int or bool to be stored

        Args:
            value (T, optional): int or bool value. Defaults to False.
        """
        self.value = value

    def __index__(self):
        return int(self.value)

    def __int__(self):
        return int(self.value)

    def __str__(self) -> str:
        return f"{int(self.value)}"

    def __repr__(self) -> str:
        return f"<TL1.{ self.__class__.__name__} object at {id(self):#x}>"

    # Math methods

    def __abs__(self) -> 'NumberBooleanMixin':
        return abs(self.value)

    def __add__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value + value)

    def __floordiv__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value // value)

    def __truediv__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value / value)

    def __mod__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value % value)

    def __mul__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value * value)

    def __neg__(self) -> 'NumberBooleanMixin':
        return type(self)( -self.value)

    def __pow__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value ** value)

    def __lshift__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value << value)

    def __rshift__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value >> value)

    def __or__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value | value)

    def __sub__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value - value)

    def __xor__(self, value:T) -> 'NumberBooleanMixin':
        return type(self)(self.value ^ value)

    # Boolean methods
    def __and__(self, value:T) -> bool:
        return bool(self.value) and value

    def __bool__(self) -> bool:
        return bool(self.value)

    def __eq__(self, value:T) -> bool:
        return self.value == value

    def __ne__(self, value:T) -> bool:
        return self.value != value

    def __not__(self) -> bool:
        return not bool(self.value)

    def __format__(self, format_spec:T) -> str:
        return f"{int(self.value)}"


class Boolean(NumberBooleanMixin):
    """
        Boolean abstraction for TL1 commands
        based in NumberBooleanMixin
    """

    def __init__(self, value:bool = False):
        """
            Instanciate the Boolean class

        Args:
            value (bool, optional): the bool value. Defaults to False.
        """
        super().__init__(value)

class Integer(NumberBooleanMixin):
    """
        Integer abstraction for TL1 commands
        based in NumberBooleanMixin
    """

    def __init__(self, value:int = 0):
        """
            Instanciate the Integer class

        Args:
            value (int, optional): the int value. Defaults to 0.
        """
        super().__init__(value)


class String:
    """
        String abstraction for TL1 commands
    """
    __slots__ = ('value',)

    def __init__(self, value:str = ''):
        self.value = value

    def __repr__(self) -> str:
        return f"<TL1.{ self.__class__.__name__} object at {id(self):#x}>"

    # Math
    def __add__(self, value:str) -> 'String':
        return type(self)(self.value.__add__(value))

    def __mod__(self, value:Union[str,tuple]) -> 'String':
        return type(self)(self.value % value)

    def __mul__(self, value:int) -> 'String':
        return type(self)(self.value * value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __rmul__(self, value:int) -> 'String':
        return type(self)(self.value * value)

    # Boolean
    def __eq__(self, value:str) -> bool:
        return self.value == value

    def __le__(self, value:str) -> bool:
        return self.value <= value

    def __ge__(self, value:str) -> bool:
        return self.value >= value

    def __lt__(self, value:str) -> bool:
        return self.value < value

    def __gt__(self, value:str) -> bool:
        return self.value < value

    def __len__(self) -> int:
        return len(self.value)

    def __getitem__(self, index) -> str:
        return self.value[index]

    def __str__(self) -> str:
        return self.value

    def __rmod__(self, value) -> 'String':
        return type(self)(self.value % value)

    def __iter__(self) -> str:
        return self.value

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        """
        Encodes the string using the specified encoding.

        This method functions similarly to the built-in `str.encode` method.

        Args:
            encoding (str, optional): The encoding format to use. Defaults to "utf-8".
            errors (str, optional): The error handling scheme. Defaults to "strict".
                Common options include "ignore" and "replace".

        Returns:
            bytes: The encoded byte representation of the string.
        """
        return self.value.encode(encoding=encoding, erros=errors)


class IPv4Address(String):
    """
        A IPv4 abstraction to verify if the IP4 address is valid
        
        Attributes:
            value (str): The IPv4 address
        
    """

    def __init__(self, value):
        """
            Create a instance of IPv4Address Type

        Args:
            value (str): valid IPv4 address
        """
        super().__init__(value)

        self.value = value
        self._validate(value)

    def _validate(self, value):
        """
        Validates and returns the IPv4 address.

        This method attempts to create an `ipaddress.IPv4Address` object from the provided value.
        If the value is a valid IPv4 address, the object is returned; 
        otherwise, an exception is raised.

        Args:
            value (str): The IPv4 address to validate.

        Returns:
            ipaddress.IPv4Address: The validated IPv4 address object.

        Raises:
            ValueError: If the provided value is not a valid IPv4 address.
        """
        return ipaddress.IPv4Address(value)

    def __setattr__(self, name, value):
        self._validate(value)
        if name == 'value':
            return super().__setattr__(name, value)

class NetworkPort(Integer):
    """
    Abstraction for a network port with range validation.

    This class is used to ensure that the port number falls within the valid range 
    of 0 to 65535.
    """


    def __init__(self, value = 0):
        """

        Args:
            value (int, optional): Integer representing the network port. Defaults to 0.

        Raises:
            PortRangeException: Throw a message indicating the port number is not valid
        """
        super().__init__(value)
        if not 0 <= value <= 65535 :
            raise PortRangeException
