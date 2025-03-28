from tl1.base import Command

from fiberhome.objects import LoginCredentials
from fiberhome.objects import ONU
from fiberhome.constants import ResponseType

class Lister(Command):
    __slots__ = ('modifiers')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modifiers = {"res_type":ResponseType.LIST}

class Login(Command):
    def __init__(self, username='', password=''):
        super().__init__("LOGIN")
        data = LoginCredentials(username, password)
        self.payload = data

class Logout(Command):
    def __init__(self):
        super().__init__("LOGOUT")


class ListShelf(Lister):
    def __init__(self):
        super().__init__("LST","SHELF")

class DeleteONU(Command):
    def __init__(self, onu:ONU):
        super().__init__('DEL', 'ONU')
        self.staging.aid = onu._get_data('olt_id', 'pon_id')
        self.payload = onu._get_data('onu_id_type', 'id')
