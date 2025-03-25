class TL1Exception(Exception):
    def __init__(self):
        super().__init__(self.message)
        
class PortRangeException(TL1Exception):
    message = 'Port number has to be between 0 and 65535'
    