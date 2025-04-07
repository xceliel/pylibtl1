from typing import Optional

from .constants import ResponseType

from tl1.base import DataBlock
from tl1.base import Parameter
from tl1.base import Response as DefaultResponse
from tl1.base import ImmutableRecord

from tl1.tl1types import (
    Integer,
    String
)

class PacketTable:
    """
    A class representing a table structure for packet data.

    This class holds the metadata and data associated with a table of packet information.
    It includes the table's title, column names, and the rows of data, which are represented as dictionaries.

    Attributes:
        title (str): The title or name of the table.
        columns (list[str]): A list of column names for the table.
        rows (list[dict]): A list of rows, where each row is a dictionary with key-value pairs corresponding to column names and cell values.

    Example:
        >>> table = PacketTable()
        >>> table.title = "Packet Information"
        >>> table.columns = ["Source", "Destination", "Protocol"]
        >>> table.rows = [{"Source": "192.168.0.1", "Destination": "192.168.0.2", "Protocol": "TCP"}]
    """
    def __init__(self):
        self.title = ''
        self.columns:list[str] = None
        self.rows:list[dict] = []

class PacketData:
    """
    A class representing packet data with metadata and a table of packet information.

    This class holds information about the packet data, including the number 
    of blocks, records, and other metadata,
    and a `PacketTable` instance containing the actual data table with the title, columns, and rows.

    Attributes:
        blocks (int): The number of blocks in the packet data (default: 0).
        number (int): The number of packets (default: 0).
        records (int): The number of records (default: 0).
        table (PacketTable): An instance of the `PacketTable` class, 
                            containing the actual table data.

    Example:
        >>> packet_data = PacketData(blocks=10, number=50, records=100)
        >>> packet_data.table.title = "Packet Records"
        >>> packet_data.table.columns = ["Source IP", "Destination IP", "Size"]
        >>> packet_data.table.rows = [{"Source IP": "192.168.1.1", "Destination IP": "192.168.1.2", "Size": 512}]
    """
    def __init__(self, blocks:int = 0, number:int = 0, records:int = 0):
        self.blocks:int = blocks
        self.number:int = number
        self.records:int = records
        self.table:PacketTable = PacketTable()


class Response(DefaultResponse):
    """
    A class representing a response, inheriting from DefaultResponse, 
        that optionally parses a datatable.

    This class extends the functionality of the DefaultResponse by adding the ability to parse 
    a tabular data structure from the response text. Depending on the response type, the datatable 
    is parsed into a structured format using the `PacketData` class.

    Attributes:
        table (PacketData | None): A PacketData instance containing the parsed table data, 
                                    or None if no table is present.
    
    Args:
        header (str): The header of the response.
        identifier (str): The identifier of the response.
        text (str): The response text, possibly containing a datatable.
        terminator (str): The terminator string for the response.
        **kwargs (dict): modifiers sent by command to give custom behavier

    
    Methods:
        parse_datatable(text: str): Parses the given response text into 
                                    a `PacketData` object containing the datatable.
    """
    __slots__ = ('result', 'res_type')
    def __init__(self, header, identifier, text, terminator, **kwargs):
        
        """
        Initializes a Response object, parsing a datatable if the response type is LIST.

        Args:
            header (str): The header of the response.
            identifier (str): The identifier of the response.
            text (str): The response text, which may contain tabular data.
            terminator (str): The terminator string for the response.
            res_type (ResponseType, optional): The type of the response. 
                                                Defaults to ResponseType.DEFAULT.

        Initializes the `table` attribute if the response type is `ResponseType.LIST`.
        """
        super().__init__(header, identifier, text, terminator)
        self.result = None

        # The first 3 characters are spaces, 
        # its checks if the beging initiates with 'total_blocks', which is a table param
        if text[3:6] == 'tot' and text:
            self.res_type = ResponseType.LIST
            self.result = self.parse_datatable(text)

        # I didn't decided about this part yet
        if self.result is None:
            self.res_type = ResponseType.DEFAULT
            text = text.strip()
            
            data = text.split('   ')
            mapped = dict( pair.split('=') for pair in data)
            maper = type('Result', (ImmutableRecord,), {'__slots__':tuple(mapped.keys()) } )
            
            self.result = maper(**dict( pair.split('=') for pair in data ))
            

    def parse_datatable(self, text):
        """
        Parses the response text to extract tabular data into a PacketData object.

        This method processes the response text to extract parameters such as the number of blocks, 
        records, and the table structure. It then dynamically 
        creates rows from the data and stores them
        in a `PacketData` instance.

        Args:
            text (str): The response text, expected to contain a tabular structure.

        Returns:
            PacketData: A structured object containing the parsed table data, 
                        including title, columns, and rows.

        Raises:
            ValueError: If the response text is not in the expected format 
                        or is missing required information.
        """

        lines = text.split('\r\n')

        params, lines = lines[:3], lines[4:]

        params = ( item.strip() for item in params )

        blocks, number, records = ( item.split('=')[1] for item in params )

        data = PacketData(int(blocks), int(number), int(records))

        # get the title and skip the horizontal line
        data.table.title, lines = lines[0], lines[2:]
        data.table.columns, lines = lines[0].split('\t'), lines[1:]

        rower = type('Row', (ImmutableRecord,), {'__slots__':data.table.columns})

        for i in range(data.records):
            cells =  zip(data.table.columns, lines[i].split('\t'))
            data.table.rows.append(rower(**dict(cells)))

        return data

class LoginCredentials(DataBlock):
    """
        TL1 Login credentials
    """
    __slots__ = ('username', 'password')

    def __init__(self, username:str='', password:str=''):
        self.username = Parameter('UN', username)
        self.password = Parameter('PWD', password)

class ONU(DataBlock):
    """
        ONU Basic representation
    """
    __slots__ = (
        'id',
        'desc',
        'olt_id',
        'pon_id',
        'onu_id_type',
        'onu_ip',
        'model'
        )

    def __init__(
        self,
        onu_id:Optional[int] = 0,
        olt_id:Optional[int] = 0,
        pon_id:Optional[str] = '',
        model:Optional[str] = ''
        ):

        self.id = Parameter('ONUID', Integer(onu_id))
        self.desc = Parameter('DESC', String(''))
        self.olt_id = Parameter('OLTID', Integer(olt_id))
        self.pon_id = Parameter('PONID', Integer(pon_id))
        self.onu_id_type = Parameter('ONUIDTYPE', Integer())
        self.onu_ip = Parameter('ONUIP', String())
        self.model = Parameter('ONUTYPE', String(model))
