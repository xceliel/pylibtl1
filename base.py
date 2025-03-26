from typing import Optional

from datetime import (
    datetime as Datetime,
    date as Date,
    time as Time
)

from constants import (
    StatusCode,
    Terminator,
    AlarmCode
)

from primitives import DataBlock

class Parameter:

    __slots__ = ('key','value')
    
    __assoc__ = '='
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def __str__(self):
        return f"{self.key}{self.__assoc__}{self.value}"
    
    def _tuple(self):
        return self.key,str(self.value)


class SlotsValues:
    __sep__ = ','
    
    def __str__(self) -> str:
        return self._parsed()

    
    def _parsed(self) -> str:
        return self.__sep__.join(
                getattr(self,i)  
                for i in self.__slots__ if getattr(self,i)
            )
    

class CommandCode(SlotsValues):
    
    __slots__ = ("verb", "mod1", "mod2")    
    __sep__ = '-'
    
    def __init__(self, verb, mod1='', mod2=''):
        self.verb:str = verb
        self.mod1:str = mod1
        self.mod2:str = mod2


class StagingBlock:
    
    __slots__ = ("tid", "aid", "ctag", "gblock")
    
    def __init__(self):
        self.tid:str = ''
        self.aid:str = ''
        self.ctag:str = 'CTAG'
        self.gblock:str = ''
    
    def __str__(self) -> str:
        return f"{self.tid}:{self.aid}:{self.ctag}:{self.gblock}"


class PayloadBlock(DataBlock):
    pass

                
class Command:
    
    __slots__ = ('command', 'staging', 'payload')
    
    def __init__(self, verb, mod1='', mod2=''):
        self.command = CommandCode(verb, mod1, mod2)
        self.staging = StagingBlock()
        self.payload = PayloadBlock()
        
    def __str__(self)  -> str:
        return f"{self.command}:{self.staging}:{self.payload};"
            
    def __bytes__(self) -> bytes:
        return bytes(self.__str__(), encoding='ascii')

    
class ResponseHeader:
    """ 
        The "VENDOR_IP YYYY-MM-DD HH:mm:ss"
        part from the response text
        
        A simple class, there no special methods with it
        
        Attributes:
            source_id (bytes): Vendor identifier
            date (datetime.date): Date when the request was made
            time (datetime.time): Time when the request was made 
    """
    
    __slots__ = ('source_id', 'date', 'time')

    def __init__(
            self, 
            sid:Optional[bytes]='', 
            date:Optional[Date] = None, 
            time:Optional[Time] = None
        ):
        self.source_id:bytes = sid
        self.date:Date = date
        self.time:Time = time


class ResponseId:
    """
        Response ID
        
        The "M CTAG COMPLD" part
        
        'There Is Nothing Special About This Board! Nothing!'
        
        Attributes:
            type (bytes): type of message, generally M
            ctag (bytes): correlation tag, 
            status (StatusCode): response status code
    """
    
    __slots__ = ('type', 'ctag', 'status')

    def __init__(
            self, 
            res_type:Optional[bytes] = 'M', 
            ctag:Optional[bytes] = 'CTAG', 
            status:Optional[StatusCode] = StatusCode.NONE
        ):
        self.type:bytes = res_type
        self.ctag:bytes = ctag
        self.status:StatusCode = status


class Response:
    """
        The Response itself
        
        
        Attributes:
            header (ResponseHeader): vendor_ip date and time
            identifier (ResponseId): response identifier with status code
            text (bytes): response text
            terminator (Terminator): Terminator constant indicanting to stop or continue
    """
    
    __slots__ = ('header', 'identifier', 'text', 'terminator')
    __type__ = 'response'

    def __init__(
            self, 
            header:Optional[ResponseHeader] = None, 
            identifier:Optional[ResponseId] = None, 
            text:Optional[bytes] = b'', 
            terminator:Optional[Terminator] = Terminator.STOP
        ):
        self.header:ResponseHeader = header
        self.identifier:ResponseId = identifier
        self.text:bytes = text
        self.terminator:Terminator = terminator


class AcknowledgmentMessage:
    """
        First, what a long and hard word for a simple thing
        Second, its the acknowledgement message class
        
    """
    __slots__ = ('code','ctag','terminator')
    
    def __init__(
            self,
            code:Optional[bytes] = b'OK',
            ctag:Optional[bytes] = b'CTAG',
            terminator:Optional[Terminator] = Terminator.STOP
        ):
        self.code:bytes = code
        self.ctag:bytes = ctag
        self.terminator:Terminator = terminator


class AutonomousIdentifier:
    
    __slots__ = ('code', 'atag', 'clause')
    
    def __init__(
        self,
        code:Optional[AlarmCode] = AlarmCode.Warn,
        atag:Optional[bytes] = b'',
        clause:Optional[list[str]] = []
    ):
        self.code:AlarmCode = code
        self.atag:bytes = atag
        self.clause:list[str] = clause


class AutonomousMessage:
    """
        A message received when things change
        In the most of cases, alarms
    """
    
    
    __slots__ = ('header', 'identifier', 'body', 'terminator')
    __type__ = 'auto'
    
    def __init__(
            self,
            header:Optional[ResponseHeader] = None,
            identifier:Optional[AutonomousIdentifier] = None,
            body:Optional[bytes] = None,
            terminator:Optional[Terminator] = Terminator.STOP
        ):
        self.header:ResponseHeader = header
        self.identifier:AutonomousIdentifier = identifier
        self.body:bytes = body
        self.terminator:Terminator = terminator