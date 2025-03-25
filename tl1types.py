from typing import TypeVar, Optional, Union

import ipaddress
from exceptions import PortRangeException

T = TypeVar('T')

class NumberBooleanMixin:
    
    __slots__ = ('value')
    
    def __init__(self, value:T = False):
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
        return self.value == value;
    
    def __ne__(self, value:T) -> bool:
        return self.value != value;
    
    def __not__(self) -> bool:
        return not bool(self.value)
    
    def __format__(self, format_spec:T) -> str:
        return f"{int(self.value)}"


class Boolean(NumberBooleanMixin):
    __slots__ = ('value')
    
    def __init__(self, value:bool = False):
        super().__init__(value)

class Integer(NumberBooleanMixin):
    __slots__ = ('value')

    def __init__(self, value:int = False):
        super().__init__(value)


class String:
    __slots__ = ('value')
    
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
        return self._value <= value
    
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
        return self.value.encode(encoding=encoding, erros=errors)


class IPv4Address(String):
    
    __slots__ = ('value')
    
    def __init__(self, value):
        # Validate IP Address
        self.value = value
        self._validate(value)
                
    def _validate(self, value):
        return ipaddress.IPv4Address(value)
        
    def __setattr__(self, name, value):
        self._validate(value)
        if name == 'value':
            return super().__setattr__(name, value)
    
class NetworkPort(Integer):
    __slots__ = ('value')
    
    def __init__(self, value = False):
        if not( 0 <= value <= 65535 ):
                raise PortRangeException
        
        super().__init__(value)
