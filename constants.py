from enum import Enum

class StatusCode(Enum):
    Completed = b'COMPLD'
    Delayed = b'DELAY'
    Denied = b'DENY'
    Partially = b'PRTL'
    Retrieved = b'RTRV'
    NONE = b'NONE'

class AlarmCode(Enum):
    Criti = b'*C'
    Major = b'**'
    Minor = b'*'
    Warn = b'A'

class Terminator(Enum):
    CONTINUE = b'>'
    STOP = b';'
    ACK = b'<'

