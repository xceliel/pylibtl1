class DataBlock:
    
    def __dict__(self) -> dict:
        return dict(
                getattr(self, item)._tuple()
                for item in self.__slots__ 
            )
        
    def __setattr__(self, name, value):
        
        _data = value
        
        if hasattr(self, name):
            _data = getattr(self, name)
            _data.value = value
            
        super().__setattr__(name, _data)



    def items(self):
        return self.__dict__()