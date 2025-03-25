from enum import Enum

class CompletionCode(Enum):
    COMPLD = 'Completed'
    DELAY = 'Delayed'
    DENY = 'Failed'
    PRTL = 'Partially'
    RTRV = 'Retrived'
    NONE = 'None'

class Terminator(Enum):
    CONTINUE = '>'
    STOP = ';'
