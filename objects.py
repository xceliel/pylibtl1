from typing import Optional

from base import DataBlock
from base import Parameter

from tl1types import (
    Boolean,
    Integer,
    String
)

class LoginCredentials(DataBlock):
    __slots__ = ('username', 'password')
    
    def __init__(self, username='', password=''):
        self.username = Parameter('UN', username)
        self.password = Parameter('PWD', password)

class ONU(DataBlock):
    
    __slots__ = (
        'id', 
        'olt_id', 
        'pon_id', 
        'onu_id_type', 
        'onu_ip'
        )
    
    def __init__(
        self, 
        onu_id:Optional[int] = 0, 
        olt_id:Optional[int] = 0, 
        pon_id:Optional[str] = ''
        ):
        
        self.id = Parameter('ONUID', Integer(onu_id))
        self.olt_id = Parameter('OLTID', Integer(olt_id))
        self.pon_id = Parameter('PONID', Integer(pon_id))
        self.onu_id_type = Parameter('ONUIDTYPE', Integer())
        self.onu_ip = Parameter('ONUIP', String())
