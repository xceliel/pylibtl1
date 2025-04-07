from enum import Enum, auto

class ResponseType(Enum):
    DEFAULT = auto()
    LIST = auto()

class WifiStandard(Enum):
    A = '802.11a'
    B = '802.11b'
    G = '802.11g'
    AC = '802.11ac'
    AN = '802.11an'
    BG = '802.11b/g'
    BGN = '802.11bgn'
    N = '802.11n'

class WifiBandwidth(Enum):
    MHZ_20 = "20MHZ"
    MHZ_20_40 = "20/40MHZ"
    MHZ_40 = "40MHZ"
    MHZ_80 = "80MHZ"

class BandWidth(Enum):
    ONE = "1G/1G"
    TEN1 = "10G/1G"
    TEN = "10G/10G"
    QUARTER8 = "2.5G/1.25G"
    TENQ = "10G/2.5G"

class WifiAuthMode(Enum):
    OPEN = "OPEN"
    SHARED = "SHARED"
    WEPAUTO = "WEPAUTO"
    WPAPSK_WPA = "WPAPSK WPA"
    WPA2PSK_WPA2 = "WPA2PSK WPA2"
    WPA_WPA2 = "WPA/WPA2"
    WPAPSK = "WPAPSK"
    WPA2PSK = "WPA2PSK"

class WifiEncryptionType(Enum):
    WEP = "WEP"
    TKIP = "TKIP"
    AES = "AES"
    TKIPAES = "TKIPAES"

class WepEncryptionLevel(Enum):
    BIT_40 = 1   # 40-bit WEP
    BIT_104 = 2  # 104-bit WEP


class ErrorCodes(Enum):
    """
    Enum representing Fiberhome TL1 error codes (EN).

    The error codes are categorized into five types, each identified by a letter 
    prefix that represents the type of error. The types are as follows:
    
    - I: Input error
    - D: Device error
    - S: System error
    - E: Exception error
    - T: Test error

    Each error code in this enumeration corresponds to a specific error type 
    and provides more granular information for troubleshooting or handling errors.
    """
    IRNE = "Resource does not exist"
    IANE = "The alarm does not exist"
    IMP = "Missing parameter"
    IIPF = "Invalid parameter format"
    IIPE = "Input parameter error"
    DDNS = "Device my not support this operation"
    DDOF = "Device operation failed"
    DDB = "Device is busy"
    SENS = "EMS may not support his operation"
    SEOF = "EMS operation failed"
    EEEH = "EMS exception happens"
    TUB = "User is busy"
    TUT = "User is testig"
    TTMB = "Test module is busy"

class WirelessArea(Enum):
    ETSI = 0
    FCC = 1
    THAILAND = 2
    PHILIPPINES = 3
    INDONESIA = 4
    BRAZIL = 5
    INDIA = 6
    ARMENIA = 7
    MALAYSIA = 8
    PAKISTAN = 9
    RUSSIA = 10
    CHINA = 11
    CHILE = 12
    EUA = 13
    MYANMAR = 14
    ECUADOR = 15
    COLOMBIA = 16
    ARGENTINA = 17
    SRI_LANKA = 18
    IRAN = 19
    YEMEN = 20
    SAUDI_ARABIA = 21
    KUWAIT = 22
    IRAQ = 23
    VIETNAM = 24