"""
    Contains primitive classes for handling TL1 operations, such as DataBlock.
"""
from typing import Optional

class DataBlock:
    """
        This class is a base to parse the slots to key=value string
        to be used in TL1 commands
        
    """
    __slots__ = ()

    __sep__ = ','
    __assoc__ = '='

    def __str__(self) -> str:
        """
        Returns a string representation of the slots as key=value pairs, 
        separated by commas.
        """
        return self.__sep__.join(
            f"{key}{self.__assoc__}{value}" 
            for key,value in self._parsed().items()
            )

    def _get_data(self, *params:Optional[list]) -> str:
        """
        Similar to `__str__`, but allows specifying which items to return.

        Args:
            *params (list, optional): A list of items to return. If no items are specified, 
                                    returns all available items.

        Returns:
            str: A string representation of the requested TL1 parameter list.
        """

        # If the parameter list is empty, return all items as TL1 parameters
        if not params:
            return str(self)

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
        """
            Return the `__slots__` fields as a dict

        Returns:
            dict: dict with `__slots__` values
        """
        return self._parsed()

    
    def _parsed(self) -> dict:
        """
            Parse the `__slots__` to dict

        Returns:
            dict: dict with `__slots__` values
        """
        return dict(
                getattr(self, item).tuple()
                for item in self.__slots__
            )
