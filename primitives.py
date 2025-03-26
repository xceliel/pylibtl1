from typing import Optional

class DataBlock:
    """
        This class is a base to parse the slots to key=value string
        to be used in TL1 commands
        
    """
    __slots__ = ()
    
    __sep__ = ','
    __assoc__ = '='
    
    def __str__(self):
        """
            This function parse the slots to key=value string separated by comma
        """
        return self.__sep__.join(
            f"{key}{self.__assoc__}{value}" 
            for key,value in self._parsed().items() 
            )
    
    def _get_data(self, *params:Optional[list]):
        """
            Do almost the same thing as __str__
            but allow to specify which items to return
            
            Attributes:
                *params (parameter list): list of items to return
                
            Returns:
                str: TL1 parameter list
        """
        
        # If the parameter list is empty, return all items as TL1 parameters
        if params == []:
            return self.__str__()
        
        # Else create a generator with the chosen items
        items_gen = ( 
            getattr(self, item) 
            for item in self.__slots__
            if item in params
            )
        
        # Return the associative list with the chosen items
        return self.__sep__.join(
            f"{item.key}{self.__assoc__}{item.value}"
            for item in items_gen
        )
    
    
    # Return the result of _parsed method
    def __dict__(self) -> dict:
        return self._parsed()        

    # Parse items to dict
    def _parsed(self):
        return dict(
                getattr(self, item)._tuple()
                for item in self.__slots__ 
            )
