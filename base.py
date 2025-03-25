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

class DataBlock:
    __slots__ = ()
    
    __sep__ = ','
    __assoc__ = '='
    
    def __str__(self):
        return self.__sep__.join(
            f"{key}{self.__assoc__}{value}" 
            for key,value in self._parsed().items() 
            )
    
    def _get_data(self, *params):
        if params == []:
            return self.__str__()
        
        items_gen = ( 
            getattr(self, item) 
            for item in self.__slots__
            if item in params
            )
        
        return self.__sep__.join(
            f"{item.key}{self.__assoc__}{item.value}"
            for item in items_gen
        )
    
    def __dict__(self) -> dict:
        return self._parsed()        

    def _parsed(self):
        return dict(
                getattr(self, item)._tuple()
                for item in self.__slots__ 
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