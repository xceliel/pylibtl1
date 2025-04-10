"""
Imports the Optional type hint from the typing module.

`Optional` is used to indicate that a value can either be of a specific type or None.
"""
from typing import Optional,  Dict, Any, Union

from datetime import (
    datetime as Datetime,
    date as Date,
    time as Time
)

from .constants import (
    ResponseType,
    StatusCode,
    Terminator,
    AlarmCode
)

from .primitives import DataBlock

class Parameter:
    """
    Abstraction for a key-value pair to be used in TL1 commands.

    This class represents a key-value pair, which can be parsed into 
    a key=value format for inclusion in TL1 commands.
    """
    __slots__ = ('key','value')

    __assoc__ = '='

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        """
        Returns a string representation of the key-value pair in 'key=value' format.

        Returns:
            str: The key-value pair as a 'key=value' string.
        """
        return f"{self.key}{self.__assoc__}{self.value}"

    def tuple(self):
        """
        Creates a tuple of the key and value for further parsing.

        Returns:
            tuple: A tuple containing the key and value.
        """
        return self.key,str(self.value)

class ParamBlock(DataBlock):
    """
    A subclass of `DataBlock` that dynamically creates `__slots__` based on
    the keyword arguments provided during initialization.
    """
    def __new__(cls, *args, **kwargs):
        """
        Dynamically define `__slots__` based on the keyword arguments passed.

        Args:
            *args: Positional arguments (not used).
            **kwargs: Keyword arguments used to dynamically define slots.

        Returns:
            ParamBlock instance with dynamically created slots.
        """
        instance = super().__new__(cls)

        slots = kwargs.keys()

        if not hasattr(instance, '__slots__'):
            instance.__slots__ = tuple(slots)
        else:
            instance.__slots__ = tuple(set(slots) | set(instance.__slots__) )

        return instance

    def __init__(self, **kwargs):
        """
        Initialize the instance by assigning values from kwargs to the dynamically
        created slots.

        Args:
            **kwargs: Keyword arguments where keys are slot names and values are slot values.
        """
        for item in self.__slots__:
            setattr(self, item, kwargs[item])
            
class SlotsValues:
    """
    A base class for managing attribute values with predefined slots.

    This class provides a way to store values in a defined set of slots and 
    offers methods for parsing and converting these values to a string representation.
    The `__sep__` attribute defines the separator used when joining slot values.

    Attributes:
        __slots__ (tuple): A tuple defining the attribute names for this class. 
                            Inherited classes can extend this tuple with additional slots.
        __sep__ (str): The separator used to join the slot values when converting to a string.
                            Default to ','.

    Methods:
        __str__(): Returns a string representation of the class, joining non-empty slot values.
        parsed(): Returns a string of non-empty slot values, separated by `__sep__`.
    """

    __slots__ = ()
    __sep__ = ','

    def __str__(self) -> str:
        """
            Returns a string of non-empty slot values, separated by `__sep__`.
            Actually a `parsed()` method wrapper
        Returns:
            str: string of non-empty slot values, separated by `__sep__`.
        """
        return self.parsed()


    def parsed(self) -> str:
        """
        
        Returns a string of non-empty slot values, separated by `__sep__`.

        Returns:
            str: string of non-empty slot values, separated by `__sep__`.
        """
        return self.__sep__.join(
                getattr(self,i)
                for i in self.__slots__ if getattr(self,i)
            )


class CommandCode(SlotsValues):
    """
    Represents a TL1 Command Code.

    This class encapsulates a command code with a verb and optional modifiers (`mod1`, `mod2`).
    The command code is typically structured as a verb followed by modifiers, separated by a hyphen.

    Attributes:
        verb (str): The primary verb of the command (e.g., 'ACT', 'DEACT').
        mod1 (str): The first modifier, used to provide additional details for the command. 
                    Default to empty string.
        mod2 (str): The second modifier, used for further specification. Default to empty string.
        __sep__ (str): The separator used to combine the verb and modifiers (default is '-').
    """
    __slots__ = ("verb", "mod1", "mod2")
    __sep__ = '-'

    def __init__(self, verb, mod1='', mod2=''):
        self.verb:str = verb
        self.mod1:str = mod1
        self.mod2:str = mod2


class StagingBlock:
    """
    Represents a TL1 Staging Block.

    This class is used to encapsulate the components of a TL1 staging block,
    which includes identifiers like `tid`, `aid`, and `ctag`, along with a
    `gblock` for grouping information.

    Attributes:
        tid (str): The transaction ID, typically a unique identifier for the transaction.
        aid (str): The action ID, used to identify the specific action in the transaction.
        ctag (str): The correlation tag, a unique identifier for correlating related messages.
        gblock (str): A grouping block identifier, used to organize related blocks.
    """
    __slots__ = ("tid", "aid", "ctag", "gblock")

    def __init__(self):
        self.tid:str = ''
        self.aid:str = ''
        self.ctag:str = 'CTAG'
        self.gblock:str = ''

    def __str__(self) -> str:
        return f"{self.tid}:{self.aid}:{self.ctag}:{self.gblock}"


class PayloadBlock(DataBlock):
    """
        Payload block abstractions
        
        This class parse its values into a payload string
        to be use with Command, to be later parsed into
        the command string according to the TL1 protocol

    """
    pass


# from TOP 10 worst ideas I had:
# 1 - \/
class Command:
    """
    Abstraction for a TL1 Protocol command.

    This class parses its values into a command string 
    that can be sent according to the TL1 protocol.
    """
    __slots__ = ('command', 'staging', 'payload', 'modifiers')
    
    __type__ = None

    def __init__(self, verb, mod1='', mod2=''):
        self.command = CommandCode(verb, mod1, mod2)
        self.staging:StagingBlock = StagingBlock()
        self.payload:PayloadBlock = PayloadBlock()
        self.modifiers = None
        
        
    def __str__(self)  -> str:
        return f"{self.command}:{self.staging}:{self.payload};"

    def __bytes__(self) -> bytes:
        return bytes(self.__str__(), encoding='ascii')

class ResponseHeader:
    """
    Represents the "VENDOR_IP YYYY-MM-DD HH:mm:ss" part of the response text.

    This is a simple class without any special methods.

    Attributes:
        source_id (str): The vendor identifier.
        date (datetime.date): The date when the request was made.
        time (datetime.time): The time when the request was made.
    """

    __slots__ = ('source_id', 'date', 'time')

    def __init__(
            self,
            sid:Optional[str]= '',
            date:Optional[Date] = None,
            time:Optional[Time] = None
        ):
        self.source_id:str = sid
        self.date:Date = date
        self.time:Time = time


class ResponseId:
    """
    Represents the "M CTAG COMPLD" part of the response.

    This is a simple class with no methods.

    Attributes:
        type (str): The type of the message, typically 'M'.
        ctag (str): The correlation tag.
        status (StatusCode): The response status code.
    """

    __slots__ = ('type', 'ctag', 'status')

    def __init__(
            self,
            res_type:Optional[str] = 'M',
            ctag:Optional[str] = 'CTAG',
            status:Optional[StatusCode] = StatusCode.NONE
        ):
        self.type:str = res_type
        self.ctag:str = ctag
        self.status:StatusCode = status


class Response:
    """
    Abstraction for a response message.

    Attributes:
        header (ResponseHeader): The vendor IP, date, and time from the response.
        identifier (ResponseId): The response identifier, including the status code.
        text (str): The body of the response message.
        terminator (Terminator): The terminator constant indicating whether to stop or continue.
        **kwargs (dict): modifiers sent by command to give custom behavier
    """
    __slots__ = ('header', 'identifier', 'text', 'terminator')
    __type__ = ResponseType.DEFAULT

    def __init__(
            self,
            header:Optional[ResponseHeader] = None,
            identifier:Optional[ResponseId] = None,
            text:Optional[str] = '',
            terminator:Optional[Terminator] = Terminator.STOP,
            **kwargs
        ):
        self.header:ResponseHeader = header
        self.identifier:ResponseId = identifier
        self.text:str = text
        self.terminator:Terminator = terminator


class AcknowledgmentMessage:
    """
    Abstraction for a response message.

    Attributes:
        code (AcknowledgmentCode): The status code of the acknowledgment.
        ctag (str): The correlation tag associated with the message.
        terminator (str): The character indicating the end of the message, typically '<'.
        **kwargs (dict): modifiers sent by command to give custom behavier    """
    __slots__ = ('code','ctag','terminator')
    __type__ = ResponseType.ACK

    def __init__(
            self,
            code:Optional[str] = 'OK',
            ctag:Optional[str] = 'CTAG',
            terminator:Optional[Terminator] = Terminator.STOP,
            **kwargs
        ):
        self.code:str = code
        self.ctag:str = ctag
        self.terminator:Terminator = terminator


class AutonomousIdentifier:
    """
    Abstraction for an autonomous message identifier, similar to ResponseId.

    Attributes:
        code (AlarmCode): The response code, typically an alarm code.
        ctag (str): The correlation tag associated with the message.
        clause (list[str]): Identifies the message type.
    """

    __slots__ = ('code', 'atag', 'clause')

    def __init__(
        self,
        code:Optional[AlarmCode] = AlarmCode.WARN,
        atag:Optional[str] = '',
        clause:Optional[list[str]] = None
    ):
        self.code:AlarmCode = code
        self.atag:str = atag
        self.clause:list[str] = clause


class AutonomousMessage:
    """
        The message received when things change
        In the most of cases, alarms
        
        Attributes:
        header (ResponseHeader): The vendor IP, date, and time from the response.
        identifier (AutonomousIdentifier): Autonomous message identification
        text (list[str]): The message content
        terminator (Terminator): The character indicating the end of the message, typically ';'.
        **kwargs (dict): modifiers sent by command to give custom behavier
    """

    __slots__ = ('header', 'identifier', 'text', 'terminator')
    __type__ = ResponseType.AUTO

    def __init__(
            self,
            header:Optional[ResponseHeader] = None,
            identifier:Optional[AutonomousIdentifier] = None,
            text:Optional[str] = None,
            terminator:Optional[Terminator] = Terminator.STOP,
            **kwargs
        ):
        self.header:ResponseHeader = header
        self.identifier:AutonomousIdentifier = identifier
        self.text:str = text
        self.terminator:Terminator = terminator

class VendorBase:
    __slots__ = ('acknowledgement', 'autonomous', 'response')

    def __init__(self):
        self.acknowledgement = self.acknowledgement or None
        self.autonomous = self.autonomous or None
        self.response = self.response or None

class VendorTL1Default(VendorBase):
    acknowledgement = AcknowledgmentMessage
    autonomous = AutonomousMessage
    response = Response

class ImmutableRecord:
    """
    A class that represents an immutable record with predefined attributes stored in __slots__.

    This class ensures that the attributes of an object are fixed and cannot be modified after
    creation. It uses __slots__ to restrict attribute assignment, providing memory efficiency.
    Attributes must be defined in __slots__, and any attempt to assign to an undefined attribute 
    will raise an AttributeError.

    Methods:
        __init__(**kwargs): Initializes an instance with values for predefined attributes.
        __iter__(): Iterates over the object's attributes, returning a (key, value) pair for each.
        __getitem__(key): Allows item-based access to the object's attributes (like a dictionary).

    Example:
        >>> record = ImmutableRecord(name="Alice", age=30)
        >>> print(record['name'])
        Alice
        >>> for key, value in record:
        >>>     print(key, value)
        name Alice
        age 30

    Attributes:
        Defined dynamically through __slots__.
    """
    __slots__ = ()

    def __init__(self, **kwargs):
        """
        Initializes an ImmutableRecord instance with values for the attributes defined in __slots__.

        Args:
            **kwargs: Keyword arguments representing the attributes and their corresponding values.
        
        Raises:
            AttributeError: If an attempt is made to set an attribute that is not in __slots__.

        Example:
            >>> record = ImmutableRecord(name="Alice", age=30)
            >>> print(record.name)  # Output: Alice
        """
        for key,value in kwargs.items():
            if key in self.__slots__:            
                setattr(self, key, value)
            else:
                raise AttributeError(f"Invalid attribute: {key}")


    def __iter__(self):
        """
        Iterates over the object's attributes and returns a (key, value) pair for each.

        Yields:
            tuple: A (key, value) pair for each attribute defined in __slots__.
        
        Example:
            >>> record = ImmutableRecord(name="Alice", age=30)
            >>> for key, value in record:
            >>>     print(key, value)
            name Alice
            age 30
        """
        return ( (key,getattr(self,key)) for key in self.__slots__ )

    def __getitem__(self, key):
        """
        Allows item-based access to the object's attributes, like a dictionary.

        Args:
            key (str): The name of the attribute to access.

        Returns:
            The value of the specified attribute.

        Raises:
            AttributeError: If the attribute does not exist in __slots__.

        Example:
            >>> record = ImmutableRecord(name="Alice", age=30)
            >>> print(record['name'])
            Alice
        """

        return getattr(self,key)

def parse_response(text:str, modifiers:dict = None, vendor:VendorBase = VendorTL1Default()):
    """
        Parse the TL1 response string into response object
    Args:
        text (str): Telnet response string

    Returns:
        response: Response object
    """
    if text[:3] != '\r\n\n':
        return None

    if modifiers is None:
        modifiers = {}

    if text[-1] == Terminator.ACK.value:
        code, ctag = text[6:].split(' ',1)
        terminator = text[-1]
        ctag = ctag[:-1]
        return vendor.acknowledgement(code, ctag, Terminator(terminator), **modifiers)


    # Remove the firsts 6 characters, they are '\r\n\n' and the spaces
    header_txt, identifier_txt, text = text[6:].split('\r\n',2)

    sid, dt_txt = header_txt.split(' ',1)
    header = ResponseHeader(sid, Datetime.fromisoformat(dt_txt))

    identifier = None
    if identifier_txt[0] == 'M':
        res_type, _, ctag, status = identifier_txt.split(' ')
        identifier = ResponseId(res_type, ctag, status)
    else:
        code, atag, clause = identifier_txt.split(' ',2)
        identifier = AutonomousIdentifier(code, atag, clause.split(' '))

    terminator = text[-1]
    text = text[:-1]

    if identifier_txt[0] != 'M':
        return vendor.autonomous(header, identifier, text, Terminator(terminator), **modifiers)

    return vendor.response(header, identifier, text, Terminator(terminator), **modifiers)

