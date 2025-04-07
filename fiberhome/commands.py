

from typing import Optional,  Dict, Any, Union
from tl1.base import Command
from tl1.base import (
    Parameter,
    ParamBlock
)

from tl1.tl1types import (
    IPv4Address,
    Boolean,
    String,
    Integer
)

from .constants import (
    WifiStandard,
    WifiBandwidth,
    BandWidth,
    WifiAuthMode,
    WifiEncryptionType,
    WepEncryptionLevel,
    WirelessArea
)

from fiberhome.objects import LoginCredentials
from fiberhome.objects import ONU


# Session Control Commands
#
# There are only 3 commands:
# Login and Logout: Self explanatory
# Handshake: Keep the session alive

class FiberhomeCommand(Command):
    """
        Base command for Fiberhome vendor

    Args:
        Command (class): Base class for TL1 commands

    Returns:
        object: an abstraction of TL1 command
    """
    __slots__ = ('access','body','_result', '__changed')
    
    def __init__(self, verb:str, mod1:Optional[str]='', mod2:Optional[str]=''):
        """
            Instantiate the parent class and
            initiate the access and body fields for later

            the arguments are to build the command name with the pattern:
                VERB-MOD1-MOD2
        Args:
            verb (str): The first command word. Required
            mod1 (str, optional): 2nd word. Defaults to ''.
            mod2 (str, optional): 3nd word. Defaults to ''.
        """
        super().__init__(verb, mod1, mod2)
        self.__changed:bool = True
        self.access:dict = {}
        self.body:dict = {}
        self._result:str = ""
    
    def _build(self):
        """
            Create to facilitate the builder pattern
            
            The access and body field are parsed in separated ParamBlock instances and
            assigned to staging.aid and payload fields respective
        
            Then process the string if the fields where changed
            to prevend process it again
        """
        self.staging.aid = ParamBlock(**self.access)
        self.payload = ParamBlock(**self.body)
        
        if not self.__changed:
            return None
        
        self._result = super().__str__()
        self.__changed = False
    
    def __setattr__(self, name, value):
        if hasattr(self, '__changed') and name != '__changed':
            super().__setattr__('__changed', True)
        return super().__setattr__(name, value)
    
    def __str__(self):
        """
            Build the string and send it to 
        """
        self._build()
        return self._result

class Login(FiberhomeCommand):
    """
        Login class, allow user to enter into a session
    """
    def __init__(self, username='', password=''):
        """
        Instantiate the Login object to handle login credentials.

        Args:
            username (str, optional): The username for the login. Defaults to an empty string.
            password (str, optional): The password for the login. Defaults to an empty string.
        """
        super().__init__("LOGIN")
        self.body = {
            "username": Parameter('UN', String(username)),
            "password": Parameter('PWD', String(password))
        }

class Logout(FiberhomeCommand):
    """
        Login class, allow user to exit into a session
    """
    def __init__(self):
        """
        Instantiate the Logout object to handle login credentials.
        
        There no args
        """
        super().__init__("LOGOUT")

class Handshake(FiberhomeCommand):
    """
        Handshake class
        
        If the TCP connection has no communication within 10 minutes. the system will initiatively
        disconnect the TCP connection. However sending a handshake command can keep it connected
    """
    def __init__(self):
        """
        Instantiate the handshake object to keep session alive
        
        """
        super().__init__("SHAKEHAND")


# Onu configuration command.
#
# Possibly the majority of commands


class BaseONUCommand(FiberhomeCommand):
    """
        Class base for the majority of ONU commands
        
        The majority of ONU Identifier have a pattern for the access identifier
        This Class bring a method to 
    """
    def _build_access_block(
        self,
        onu_ip:str = None,
        olt_id:str = None,
        pon_id:str = None,
        onu_id_type:str = None,
        onu_id:str = None
    ):
        """
        
        Create access identifier for ONU

        Args:
            onu_ip (str, optional): ONU Ip Address
            olt_id (str, optional): OLT Ip address
            pon_id (str, optional): rack-shelf-slot-pon port. If any information is not available, enter NA instead
            onu_id_type (str, optional): type of identification. (ONU_NAME, MAC, LOID, ONU_Number) 
            onu_id (str, optional): ONU identifier. used for uniquely identifying the ONU connected to the PON port.
                According with the value specified in onu_id_type

        Raises:
            AttributeError: Thrown if ONU Ip or Olt Id, PON, Id, ONU Id Type and ONU Id are not specified

        Returns:
            dict[Parameter]: ONU Identifier in a dict
        """

        if onu_ip:
            return { 
                'onu_ip': Parameter('ONUIP', IPv4Address(onu_ip))
            }
        elif olt_id and pon_id and onu_id_type and onu_id:
            return {
                'olt_id': Parameter('OLTID', IPv4Address(olt_id)),
                'pon_id': Parameter('PONID', String(pon_id)),
                'onu_id_type': Parameter('ONUIDTYPE', String(onu_id_type)),
                'onu_id': Parameter('ONUID', String(onu_id))
            }
        else:
            raise AttributeError('Invalid ONU identification parameters. Please provide either "onu_ip" or a valid combination of "olt_id", "pon_id", "onu_id_type", and "onu_id"')


class AddONU(BaseONUCommand):
    """
        Authentication ONU class, used to create 
        the command to authenticate the ONU
    """
    def __init__(
            self,
            olt_id:str,
            pon_id:str,
            onu_id:str,
            model:str,
            **optionals
        ):
        """

        Create a Add ONU command instance

        Args:
            olt_id (str): OLT Ip
            pon_id (str): rack-shelf-slot-pon port. If any information is not available, enter NA instead
            onu_id (str): ONU Identifier, normally the FHTT
            model (str): ONU model. Example AN5506-01-A1
            auth_type (str, optional): Type of authentication
            password (str, optional): ONU password
            onu_number (int, optional): Index of ONU in the pon port
            name (str, optional): Name indentifying the ONU
            description (str, optional): A short description of ONU
            bandtype (str, optional): ONU bandwidth 
        """
        super().__init__('ADD','ONU')
        optional_params = {
            'auth_type': {
                'name':'AUTHTYPE',
                'type':String
            },
            'password': {
                'name':'PWD',
                'type':String
            }, 
            'onu_number':{
                'name':'ONUNO',
                'type':Integer
            },
            'name': {
                'name':'NAME',
                'type':String
            },
            'description':{
                'name':'DESC',
                'type':String
            },
            'bandtype': {
                'name':'BANDTYPE',
                'type':String
            }
        }

        required = ParamBlock(
            olt_id=Parameter('OLTID', IPv4Address(olt_id)),
            pon_id=Parameter('PONID', String(pon_id)),
            onu_id=Parameter('ONUID', String(onu_id)),
            model=Parameter('ONUTYPE', String(model))
        )

        options_block = {}

        for key, value in optionals.items():
            if key not in optional_params:
                raise ValueError(f"Invalid optional parameter: {key}")

            meta = optional_params[key]
            options_block[key] = Parameter(meta['name'], meta['type'](value))

        op_params_block = ParamBlock(**options_block) if options_block else None

        payload_parts = [str(required._get_data('onu_id', 'model'))]

        if op_params_block:
            payload_parts.append(str(op_params_block))

        self.staging.aid = required._get_data('olt_id', 'pon_id')
        self.payload = ','.join(payload_parts)

class ConfigONU(FiberhomeCommand):
    """
    
    Modify the ONU authentication mode and
    authentication ID information when replacing an ONU.

    """
    def __init__(
            self,
            olt_id:str,
            pon_id:str,
            onu_id_type:str,
            onu_id:str,
            auth_type:str = "LOID",
        ):
        """
        Modify specified ONU Authentication

        You can specify the Authentication info with the set_auth_info method

        Args:
            olt_id (str): OLT IP address
            pon_id (str): rack-shelf-slot-pon port. If any information is not available, enter NA instead
            onu_id_type (str): type of identification. (ONU_NAME, MAC, LOID, ONU_Number) 
            onu_id (str): ONU identifier. used for uniquely identifying the ONU connected to the PON port.
                        According with the value specified in onu_id_type
            auth_type (str): Authentication mode. Default LOID.(MAC, LOID, LOIDONCEON, PASSWORD)
            auth_info (Optional[str], optional): LOID or MAC address of ONU. Defaults to None.
        """
        super().__init__('CFG', 'ONU')
        
        
        self.access = {
            "olt_id": Parameter('OLTID', IPv4Address(olt_id)),
            "pon_id": Parameter('PONID', String(pon_id)),
            "onu_id_type": Parameter('ONUIDTYPE', String(onu_id_type)),
            "onu_id": Parameter('ONUID', String(onu_id))
        }
        
        self.body = {
            'auth_type': Parameter('AUTHTYPE', String(auth_type))
        }
        
    
    def set_auth_info(self, auth_info:str):
        self.body.update({
            'auth_info':  Parameter('AUTHINFO', String(auth_info))
        })


class ConfONUBandwidth(BaseONUCommand):
    """
    Set upliink and downlink bandwidth template in the ONU
    """
    def __init__(
            self,
            onu_ip:Optional[str] = None,
            olt_id:Optional[str] = None,
            pon_id:Optional[str] = None,
            onu_id_type:Optional[str] = None,
            onu_id:Optional[str]  = None,
            up_bandwidth:str = None
        ):
        """
        Configures the uplink and downlink bandwidth templates for an ONU.

        The templates must be pre-configured in the EMS before being set to the ONU.

        and the ONU need to be identified with either by IP or by OLT/pon_id/onu_id_type/onu_id

        Attributes:
            onu_ip (Optional[str]): IP address of the manageable ONU.
            olt_id (Optional[str]): IP address of the OLT.
            pon_id (Optional[str]): Rack-shelf-slot-PON port identifier.
            onu_id_type (Optional[str]): ONU identifier type (e.g., ONU_NAME, MAC, LOID, ONU_NUMBER).
            onu_id (Optional[str]): ONU identifier, depending on the chosen `onu_id_type`.
            up_bandwidth (str): Uplink DBA bandwidth template name.

        Raises:
            AttributeError: If the ONU identification parameters are incorrect or incomplete.
        """
        super().__init__('CFG', 'ONUBW')
        

        if up_bandwidth is None:
            raise AttributeError('up_bandwidth is required')

        self.access = self._build_access_block(onu_ip, olt_id, pon_id, onu_id_type, onu_id)

        self.body = {
            'up_bandwidth': Parameter('UPBW', String(up_bandwidth))
        }
        
    def set_down_bandwidth(self, down_bandwidth:str):
        """
        Set Down Bandwidth template

        Args:
            down_bandwidth (str): down bandwidth template name
        """
        self.body.update({
            'down_bandwidth': Parameter('DOWNBW', String(down_bandwidth))
        })
        

class DeleteONU(FiberhomeCommand):
    def __init__(
            self,
            olt_id:str,
            pon_id:str,
            onu_id_type:str,
            onu_id:str
        ):
        """
        Deletes the ONU authorized by the OLT
            
        Warning: Deleting ONU will also delete the services that the ONU Bears
        To re-provision such services, add and configura them again
        

        Args:
            old_id (str): OLT IP address
            pon_id (str): rack-shelf-slot-pon port. If any information is not available, enter NA instead
            onu_id_type (str): type of identification. (ONU_NAME, MAC, LOID, ONU_Number) 
            onu_id (str): ONU identifier. used for uniquely identifying the ONU connected to the PON port.
                        According with the value specified in onu_id_type
        """
        super().__init__('DEL', 'ONU')
        
        self.access = {
            "olt_id": Parameter('OLTID', IPv4Address(olt_id)),
            "pon_id": Parameter('PONID', String(pon_id))
        }
        
        self.body = {
            "onu_id_type": Parameter('ONUIDTYPE', String(onu_id_type)),
            "onu_id": Parameter('ONUID', String(onu_id))
        }


class ConfigLanPortMacLimit(FiberhomeCommand):
    """
        Configure the limit of MAC addresses for a ONU lan port

    Args:
        Command (_type_): _description_
    """
    def __init__(
        self,
        olt_id:str,
        pon_id:str,
        onu_id_type:str,
        onu_id:str,
        onu_port:int,
        count:int
        ):
        """

        Set the limit of MAC Addresses for a LAN por of a ONU.

        Args:
            old_id (str): OLT IP address
            pon_id (str): rack-shelf-slot-pon port. If any information is not available, enter NA instead
            onu_id_type (str): type of identification. (ONU_NAME, MAC, LOID, ONU_Number) 
            onu_id (str): ONU identifier. used for uniquely identifying the ONU connected to the PON port.
                        According with the value specified in onu_id_type
            onu_port (int): The ONU port to be configured
            count (int): The limit of MAC addresses between 0 and 65536
        """
        super().__init__('CFG', 'LANPORTMACLIMIT')
        self.access = {
            "olt_id": Parameter('OLTID', IPv4Address(olt_id)),
            "pon_id": Parameter('PONID', String(pon_id)),
            "onu_id_type": Parameter('ONUIDTYPE', String(onu_id_type)),
            "onu_id": Parameter('ONUID', String(onu_id)),
            "onu_port": Parameter('ONUPORT', String(f"NA-NA-NA-{onu_port}"))
        }

        self.body = {
            "count": Parameter('COUNT', Integer(count))
        }


class ConfigWifiService(BaseONUCommand):
    """
    Class to configure the Wi-Fi service on an ONU device.

    This class abstracts the configuration of a Wi-Fi service for ONU devices, allowing users to specify 
    various parameters such as frequency, wireless area, SSID, encryption types, and more to customize 
    the Wi-Fi service.

    It constructs and sends a TL1 command based on the provided parameters to configure the Wi-Fi settings on the device.
    """
    def __init__(
        self,
        onu_ip: Optional[str] = None,
        olt_id: Optional[str] = None,
        pon_id: Optional[str] = None,
        onu_id_type: Optional[str] = None,
        onu_id: Optional[str] = None,
        frequency: str = '2.4GHZ',
        enable: bool = True,
    ):
        """
        Configure Wi-Fi service for an ONU device. The ONU can be identified either
        by its IP address or by the OLT ID, PON ID, ONU ID Type, and ONU ID combination.

        Args:
            onu_ip (str, optional): The IP address of the manageable ONU. If this is provided, 
                                     other identification parameters (olt_id, pon_id, onu_id_type, onu_id) are not needed.
            olt_id (str, optional): The IP address or ID of the OLT. Required if `onu_ip` is not provided.
            pon_id (str, optional): PON port location (rack-shelf-slot-PON). Required if `onu_ip` is not provided.
            onu_id_type (str, optional): ONU identifier type (e.g., ONU_NAME, MAC, LOID, ONU_NUMBER). 
                                          Required if `onu_ip` is not provided.
            onu_id (str, optional): ONU identifier based on the selected `onu_id_type`. Required if `onu_ip` is not provided.
            frequency (str, optional): Working frequency for the Wi-Fi service. Must be either '2.4GHZ' or '5.8GHZ'. Defaults to '2.4GHZ'.
            enable (bool, optional): Enable or disable the Wi-Fi service. Possible values: `True` or `False`. 
                                      If not specified, the default is disabled (`False`).
        Raises:
            ValueError: If the frequency is not '2.4GHZ' or '5.8GHZ'.
            AttributeError: If invalid ONU identification parameters are provided (either `onu_ip` or a valid combination of `olt_id`, `pon_id`, `onu_id_type`, and `onu_id` must be provided).
        """
        super().__init__('CFG', 'WIFISERVICE')

        # Initialize the access block
        self.access = self._build_access_block(onu_ip, olt_id, pon_id, onu_id_type, onu_id)

        # Validate the frequency
        self._validate_frequency(frequency)

        parameters_block = {
            'enable': Parameter('ENABLE', Boolean(enable)),
            'working-frequency': Parameter('WORKINGFREQUENCY', String(frequency))
        }
        
        # Set the payload and staging information
        self.body = parameters_block

    def set_wireless(
        self, 
        area:WirelessArea = WirelessArea.BRAZIL, 
        power:int = 200, 
        channel:int = 0, 
        standard:WifiStandard = WifiStandard.BGN, 
        frequency:WifiBandwidth = WifiBandwidth.MHZ_20
        ):
        """
        Set Wireless parameters

        Args:
            wireless_area (int, optional): Wireless country area. Default 'BRAZIL'
            power (int, optional): The Wi-Fi power level. Possible values are from 20 to 200, in increments of 20. Default is `None`.
            wireless_channel (int, optional): Wireless channel number between 0 and 13. Default is `0`.
            wireless_standard (str, optional): Set which 802.11 wireless standard to use. 
            frequency_bandwidth (str, optional): The frequency bandwidth. 

        Returns:
            object: ConfigWifiService instance
        """
        
        tmp = {}
        
        if not isinstance(area, WirelessArea):
            raise AttributeError('The Wifi area need to be a WirelessArea value')
        
        tmp['wireless_area'] = Parameter('WILESSAREA', Integer(area.value))
        
        if not isinstance(power, int) or not power == 0 or not power % 20 != 0:
            raise AttributeError('The power need to be 0 or a number multiple of 20, between 0 and 200')
        
        tmp['power'] = Parameter('T-POWER', Integer(power))
        
        if channel < 0 and channel > 13:
            raise AttributeError('The channel value need to be a number between 0 and 13')
        
        tmp['wireless_channel'] = Parameter('WILESSCHANNEL', Integer(channel))
        
        if not isinstance(frequency, WifiBandwidth):
            raise AttributeError('The Wifi bandwidth frequency need to a WifiBandwidth value')
        
        tmp['frequency_bandwidth'] = Parameter('FREQUENCYBANDWIDTH', Integer(frequency.value))
        

#        'wireless_standard': Parameter('WILESSSTANDARD', String(standard)),


        
        self.body = {
            **self.body,
            **tmp
        }
        
        return self
        

    def set_ssid(self, ssid:int = 1, name:str = '' , enabled:bool = True, visible:bool = True):
        """
        Configure SSID 

        Args:
            ssid (int, optional): SSID index, between 1 and 4, which specifies which SSID configuration to modify. Default is `1`.
            name (str, optional): The name of the SSID (up to 32 characters). Default is `None`.
            enabled (bool, optional): Enable or disable the SSID. Possible values: `True` (enabled) or `False` (disabled). Default is `True`.
            visible (bool, optional): Indicates whether the SSID should be visible to devices. 
                                        Possible values: `True` (visible) or `False` (hidden). Default is `True`.
        Returns:
            object: ConfigWifiService instance
        """
        
        tmp = {}
        
        if not isinstance(ssid, int) or ssid > 4 and ssid < 1:
            raise AttributeError('The SSID should be a number between 1 and 4')
        
        tmp['ssid'] = Parameter('SSID', Integer(ssid))
        
        if not isinstance(name, str) or not name.isascii():
            raise AttributeError('The ')
            
        
        self.body = {
            **self.body,
            'ssid': Parameter('SSID', Integer(ssid)),
            'ssid_enabled': Parameter('SSIDENABLE', Boolean(enabled)),
            'ssid_name': Parameter('SSIDNAME', String(name)),
            'ssid_visible': Parameter('SSIDVISIBALE', Boolean(visible))
        }
        
        return self

    def set_auth(
        self, 
        password:str = None, 
        mode:WifiAuthMode = WifiAuthMode.OPEN, 
        etype:WifiEncryptionType = WifiEncryptionType.AES, 
        level:WepEncryptionLevel = WepEncryptionLevel.BIT_40
        ):
        """
        Configure the wifi authentication

        Args:
            preshared_key (str, optional): WPA pre-shared key, AKA Wi-Fi password (max 64 characters)
            mode (str, optional): The authentication mode for the WLAN. 
            type (str, optional): The encryption type for the WLAN.
            level (int, optional): The WEP encryption level. Possible values are `1` for 40-bit or `2` for 104-bit WEP. 
                                                  Default is 1.

        Returns:
            object: ConfigWifiService instance
            
        Raise:
            AttributeError: If it's not using the constant value
        """
        tmp = {}
        if password is not None:
            tmp['preshared_key'] = Parameter('PRESHAREDKEY', String(password))
            
        if not isinstance(mode, WifiAuthMode):
            raise AttributeError('The Wifi authmode need to be a WifiAuthMode value')
        
        tmp['auth_mode'] = mode.value
        
        if not isinstance(etype, WifiEncryptionType):
            raise AttributeError('The Wifi encryption type need to be a WifiEncryptionType value')
        
        tmp['encryption'] = Parameter('ENCRYPTYPE', String(etype.value))
        
        if not isinstance(level, WepEncryptionLevel):
            raise AttributeError('The Wifi encryption level need to be a WepEncryptionLevel value or the number 1 or 2')
        
        tmp['wep_encryption_level'] = Parameter('WEPENCRYPTIONLEVEL', String(level.value))
        
        self.body = {
            **self.body,
            **tmp
        }
        
        return self
    
    def update_wapkey_interval(self, interval):
        """_summary_

        Args:
            interval (int, optional): The WPA key update interval, in seconds. The value can range from 0 to 4194303. Default is `None`.

        Returns:
            object: ConfigWifiService instance
        """
        self.body['update_key_interval'] = Parameter('UPDATEKEYINTERVAL', String(interval))
        
        return self
    
    def set_wepkey(self, index, key1, key2, key3, key4):
        """
        Configure WEP Keys parameters

        Args:
            wep_key_index (int, optional): The WEP key index, between 1 and 4. Default is `None`.
            wep_key1 (str, optional): The first WEP key (up to 64 characters). Default is `None`.
            wep_key2 (str, optional): The second WEP key (up to 64 characters). Default is `None`.
            wep_key3 (str, optional): The third WEP key (up to 64 characters). Default is `None`.
            wep_key4 (str, optional): The fourth WEP key (up to 64 characters). Default is `None`.
        Returns:
            object: ConfigWifiService instance
        """
        self.body = {
            **self.body,
            'wep_key_index': Parameter('WEPKEYINDEX', Integer(index)),
            'wep_key1': Parameter('WEPKEY1', String(key1)),
            'wep_key2': Parameter('WEPKEY2', String(key2)),
            'wep_key3': Parameter('WEPKEY3', String(key3)),
            'wep_key4': Parameter('WEPKEY4', String(key4)),
        }
        
        return self
    
    def set_radius(self, server, port, key):
        """_summary_

        Args:
            server (str, optional): The RADIUS server address. Default is `None`.
            port (str, optional): The RADIUS server port (2-character string). Default is `None`.
            key (str, optional): The RADIUS key (up to 32 characters). Default is `None`.

        Returns:
            object: ConfigWifiService instance
        """
        self.body = {
            **self.body,
            'radius_server': {'name': 'RADIUSSERVER', 'type': String},
            'radius_port': {'name': 'RADIUSPORT', 'type': String},
            'radius_key': {'name': 'RADIUSKEY', 'type': String},
        }
        return self    

    def _validate_frequency(self, frequency):
        """
        Validates that the provided frequency is either '2.4GHZ' or '5.8GHZ'.
        """
        if frequency not in ['2.4GHZ', '5.8GHZ']:
            raise ValueError('The working frequency must be either "2.4GHZ" or "5.8GHZ"')



class ModifyWifiService(Command):
    """
    Class to modify the Wi-Fi service configuration on an ONU device.

    This class abstracts the modification of an existing Wi-Fi service for ONU devices, allowing users to modify
    various parameters such as frequency, wireless standard, SSID, encryption types, and more.
    """

    def __init__(
        self,
        olt_ip: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        frequency: str = '2.4GHZ',
        **optional
    ):
        """
        Modify WIFI service configuration
        
        Args:
            olt_ip (str): IP address of the OLT.
            pon_id (str): Rack-shelf-slot-PON port identifier.
            onu_id_type (str): ONU identifier type (e.g., ONU_NAME, MAC, LOID, ONU_NUMBER).
            onu_id (str): ONU identifier, depending on the chosen `onu_id_type`.
            frequency (str, optional): Working band, 5.8ghz or 2.4ghz. Defaults to '2.4GHZ'.
            enable (bool, optional): Enables or disables the function.
            wireless_area (int, optional): Wireless area, between 0 and 23, 
                                            The value will be converted to the corresponding area name.
            wireless_channel (int, optional): Wireless channel number.
            wireless_standard (str, optional): The wireless standard (e.g., 802.11b, 802.11g, 802.11b/g, 802.11n, etc.)
            power (int, optional): The Wi-Fi power, from 20 to 200, in steps of 20.
            ssid (int, optional): SSID index, 1 to 4, the ID of SSID configuration to be modified.
            ssid_enabled (bool, optional): Enable/Disable SSID.
            ssid_name (str, optional): Name of the SSID.
            ssid_visible (bool, optional): Whether the SSID is visible (1) or hidden (0).
            auth_mode (str, optional): Authentication mode for WLAN.
            encryption (str, optional): Encryption type for WLAN.
            preshared_key (str, optional): Pre-shared key for WPA.
            frequency_bandwidth (str, optional): Frequency bandwidth (e.g., 20MHz, 40MHz, 80MHz).

        Raises:
            AttributeError: If invalid ONU identification parameters are provided.
            AttributeError: If the working frequency is neither 2.4GHz nor 5.8GHz.
            ValueError: If an invalid optional parameter is provided.
        """
        super().__init__('MODIFY', 'WIFISERVICE')

        # Prepare the access parameters (OLTID, PONID, ONUIDTYPE, and ONUID)
        access = {
            'olt_ip': Parameter('OLTID', IPv4Address(olt_ip)),
            'pon_id': Parameter('PONID', String(pon_id)),
            'onu_id_type': Parameter('ONUIDTYPE', String(onu_id_type)),
            'onu_id': Parameter('ONUID', String(onu_id)),
        }

        # Validate frequency input
        if frequency != '2.4GHZ' and frequency != '5.8GHZ':
            raise AttributeError('The working frequency must be 2.4GHz or 5.8GHz')

        # Define optional parameters and their types
        optional_parameters = {
            'enable': {'name': 'ENABLE', 'type': Boolean},
            'wireless_standard': {'name': 'WILESSSTANDARD', 'type': String},
            'working_frequency': {'name': 'WORKINGFREQUENCY', 'type': String},
            'frequency_bandwidth': {'name': 'FREQUENCY-BANDWIDTH', 'type': String},
            'wireless_area': {'name': 'WILESSAREA', 'type': Integer},
            'wireless_channel': {'name': 'WILESSCHANNEL', 'type': Integer},
            'power': {'name': 'T-POWER', 'type': Integer},
            'ssid': {'name': 'SSID', 'type': Integer},
            'ssid_enabled': {'name': 'SSIDENABLE', 'type': Boolean},
            'ssid_name': {'name': 'SSIDNAME', 'type': String},
            'ssid_visible': {'name': 'SSID-VISIBALE', 'type': Boolean},
            'auth_mode': {'name': 'AUTHMODE', 'type': String},
            'encryption': {'name': 'ENCRYPTYPE', 'type': String},
            'preshared_key': {'name': 'PRESHAREDKEY', 'type': String},
        }

        # Collect all optional parameters into a dictionary
        parameters_block = Command._process_optional_parameters(optional, optional_parameters)
        # Set the access and payload (parameters_block)
        self.staging.aid = ParamBlock(**access)
        self.payload = ParamBlock(**parameters_block)


class DeleteWifiService(Command):
    """
    Class to delete the Wi-Fi service configuration on an ONU device.

    This class abstracts the removal of an existing Wi-Fi service for ONU devices, allowing users to delete
    specific Wi-Fi configurations based on the ONU's parameters like IP, OLT, PON, and SSID.
    """

    def __init__(
        self,
        onu_ip: Optional[str] = None,
        olt_id: Optional[str] = None,
        pon_id: Optional[str] = None,
        onu_id_type: Optional[str] = None,
        onu_id: Optional[str] = None,
        working_frequency: str = '2.4GHZ',
        ssid_no: Optional[int] = None
    ):
        """
        Delete WIFI service configuration
        
        Args:
            onu_ip (str, optional): IP address of the manageable ONU.
            olt_id (str, optional): IP address of the OLT.
            pon_id (str, optional): Rack-shelf-slot-PON port identifier.
            onu_id_type (str, optional): ONU identifier type (e.g., ONU_NAME, MAC, LOID, ONU_NUMBER).
            onu_id (str, optional): ONU identifier, depending on the chosen `onu_id_type`.
            working_frequency (str, optional): Working frequency (2.4GHz or 5.8GHz). Defaults to '2.4GHZ'.
            ssid_no (int, optional): SSID number to be deleted. The value should be between 1 and 4.

        Raises:
            AttributeError: If invalid ONU identification parameters are provided.
            ValueError: If ssid_no is not provided or is invalid.
            AttributeError: If the working frequency is neither 2.4GHz nor 5.8GHz.
        """
        super().__init__('DEL', 'WIFISERVICE')

        # Prepare the access parameters (ONUIP, OLTID, PONID, ONUIDTYPE, ONUID)
        access = {}

        if onu_ip:
            access['onu_ip'] = Parameter('ONUIP', IPv4Address(onu_ip))
        elif olt_id and pon_id and onu_id_type and onu_id:
            access['olt_id'] = Parameter('OLTID', IPv4Address(olt_id))
            access['pon_id'] = Parameter('PONID', String(pon_id))
            access['onu_id_type'] = Parameter('ONUIDTYPE', String(onu_id_type))
            access['onu_id'] = Parameter('ONUID', String(onu_id))
        else:
            raise AttributeError('Invalid ONU identification parameters. Please provide either "onu_ip" or a valid combination of "olt_id", "pon_id", "onu_id_type", and "onu_id"')

        # Validate frequency input
        if working_frequency != '2.4GHZ' and working_frequency != '5.8GHZ':
            raise AttributeError('The working frequency must be 2.4GHz or 5.8GHz')

        # Validate SSID number
        if ssid_no is None or ssid_no < 1 or ssid_no > 4:
            raise ValueError('Invalid SSID number. It must be between 1 and 4.')

        # Define optional parameters
        parameters_block = ParamBlock(
            working_frequency = Parameter('WORKINGFREQUENCY', String(working_frequency)),
            ssid_no = Parameter('SSIDNO', Integer(ssid_no))
        )


        # Set the access and payload (parameters_block)
        self.staging.aid = ParamBlock(**access)
        self.payload = parameters_block

class SetWanService(Command):
    """
    Class to create wan service configuration on an ONU device.

    This class abstracts the removal of an existing Wi-Fi service for ONU devices, allowing users to delete
    specific Wi-Fi configurations based on the ONU's parameters like IP, OLT, PON, and SSID.
    """
    def __init__(
        self,
        onu_ip: Optional[str] = None,
        olt_id: Optional[str] = None,
        pon_id: Optional[str] = None,
        onu_id_type: Optional[str] = None,
        onu_id: Optional[str] = None,
        status: int = 1,
        mode: int = 2,
        connection_type:int = 2,
        **options
        ):
        """_summary_

        Args:
            onu_ip (str, optional): IP address of the manageable ONU.
            olt_id (str, optional): IP address of the OLT.
            pon_id (str, optional): Rack-shelf-slot-PON port identifier.
            onu_id_type (str, optional): ONU identifier type (e.g., ONU_NAME, MAC, LOID, ONU_NUMBER).
            onu_id (str, optional): ONU identifier, depending on the chosen `onu_id_type`.
            status (int, optional): Set edit mode, 1 - Configure, 2 - Delete. Defaults to 1.
            mode (int, optional): Wan connection mode 1 to 9 or 100. The options are
                - 1-TR069 
                - 2-INTERNET 
                - 3-TR069_INTERNET 
                - 4-Multicast 
                - 5-VOIP 
                - 6-VOIP_INTERNET 
                - 7-IPTV 
                - 8-RADIUS 
                - 9-RADIUS_INTERNET 
                - 100 - Other
                Defaults to 2.
            connection_type (int, optional): Wan connection type. The options are
                - 1 - Bridge
                - 2 - Route
                Defaults to 2.
            vlan (int, optional): Wan vlan 1 to 4085.
            cos (int, optional): 802.1p priority of the WAN connection
            qos (int, optional): Wan connection QoS. 1 - Enable. 2 - Disable
            nat (int, optional): Wan connection NAT. 1 - Enable. 2 - Disable
            ip_mode (int, optional): Set Wan connection mode
                - 1 - DHCP
                - 2 - STATIC
                - 3 - PPPOE
            wan_ip (str, optional): Wan IP4 address
            wan_mask (str, optional): Wan IP4 mask
            wan_gateway (str, optional): Wan IP4 gateway
            dns_primary (str, optional): Primary DNS 
            dns_secondary (str, optional): Secondary DNS
            ip_stack (str, optional): Set the IP Stack. If its IPv4, IPv6 or Both.
                - 0 - IPv4
                - 1 - IPv4 and IPv6
                - 2 - IPv6
            ipv6_type (int, optional): Set Address source of the IPv6. 0 - DHCPv6, 1 - SLAAC
            ipv6_address (str, optional): Set WAN IPv6 address 
            ipv6_gateway (str, optional): Set WAN IPV6 gateway
            ipv6_dns1 (str, optional): Set WAN IPv6 primary dns
            ipv6_dns2 (str, optional): Set WAN IPv6 secondary dns
            ipv6_prefix (str, optional): Set WAN IPv6 prefix pool of a wan connection
            pppoe_proxy (str, optional): Set if enable a PPPoE Proxy
            pppoe_user (str, optional): Set PPPoE username
            pppoe_password (str, optional): Set PPPoE password
            pppoe_name (str, optional): Set service name
            pppoe_auth_mode (str, optional): Set PPPOE authenticate mode
                - 0 - Auto
                - 1 - CHAP
                - 2 - MS-CHAP
                - 3 - PAP
            pppoe_mode (int, optional): Set PPPoE dial-up mode
                - 1 - auto connect
                - 2 - connect when have payload
                - 3 - connect manually
            pppoe_idletime (int, optional): Set PPPoE automatic offline time. from 0 to 2000 in sec
            uport (int, optional): Set ethernet port. from 0 to 5
                - 0 - All Lan ports
                - 1 - LAN1
                - 2 - LAN2
                - 3 - LAN3
                - 4 - LAN4
                - 5 - 10G LAN
            ssid_ports (int, optional): Set ssid port, from 1 to 8.
                                        1 to 4 to specify the 2.4ghz SSID ports and
                                        5 to 8 to specify the 5Ghz SSID ports
            vlan_mode (int, optional): Vlan mode, values 1 and 3, 1 - Tagged, 3 - transparent.
            trans_state (bool, optional): Set translate status. True or False
            trans_value (int, optional): Set VID after translation. 0 to 4085
            trans_cos (int, optional): Set PON priority or COS.
            qinq_state (bool, optional): Set QinQ state. True or False
            tag_protocol_id (int, optional): Set tag protocol identifier, between 0 and 0xfffe.
            svlan (int, optional): Set SVlan, must be configured when QinQ is set. Value need to be between 1 and 4085.
            qinq_cos (int, optional): Set QinQ PON priority or COS. Between 0 and 7
            dhcp_remote_id (str, optional): Address of DHCP remote identifier
            upnp (bool, optional): enable/disable UPNP.
            activation (bool, optional): activate/deactivate. Default False.
            gemport (int, optional): Gemport value. 1 to 4096.
        Raises:
            AttributeError: _description_
        """
        super().__init__('SET','WANSERVICE')
        access = {}

        if onu_ip:
            access['onu_ip'] = Parameter('ONUIP', IPv4Address(onu_ip))
        elif olt_id and pon_id and onu_id_type and onu_id:
            access['olt_id'] = Parameter('OLTID', IPv4Address(olt_id))
            access['pon_id'] = Parameter('PONID', String(pon_id))
            access['onu_id_type'] = Parameter('ONUIDTYPE', String(onu_id_type))
            access['onu_id'] = Parameter('ONUID', String(onu_id))
        else:
            raise AttributeError('Invalid ONU identification parameters. Please provide either "onu_ip" or a valid combination of "olt_id", "pon_id", "onu_id_type", and "onu_id"')



        optional_parameters = SetWanService._init_options()
        
        options_block = Command._process_optional_parameters(options, optional_parameters)
                
        options_block.update({
            'status' : Parameter('STATUS', Integer(status)),
            'mode': Parameter('MODE', Integer(mode)),
            'connection_type': Parameter('CONNTYPE', Integer(connection_type))
        })
        
        self.staging.aid = ParamBlock(**access)
        self.payload = ParamBlock(**options_block)
    
    @staticmethod
    def _init_options():
        return {
            'vlan': { 'name':'VLAN', 'type': Integer },
            'cos': { 'name': 'COS', 'type': Integer },
            'qos': { 'name': 'QOS', 'type': Integer },
            'nat': { 'name': 'NAT', 'type': Integer },
            'ip_mode': { 'name': 'IPMODE', 'type': Integer },
            'wan_ip': { 'name': 'WANIP', 'type': IPv4Address },
            'wan_mask': { 'name': 'WANMASK', 'type': IPv4Address },
            'wan_gateway': { 'name': 'WANGATEWAY', 'type': IPv4Address },
            'dns_primary': { 'name': 'MASTERDNS', 'type': IPv4Address },
            'dns_secondary': { 'name': 'SLAVEDNS', 'type': IPv4Address },
            'ip_stack': { 'name': 'IPSTACKMODE', 'type': Integer },
            'ipv6_type': { 'name': 'IP6SRCTYPE', 'type': Integer },
            'ipv6_address': { 'name': 'IP6ADDRESS', 'type': String },
            'ipv6_gateway': { 'name': 'IP6GATEWAY', 'type': String },
            'ipv6_dns1': { 'name': 'IP6MASTERDNS', 'type': String },
            'ipv6_dns2': { 'name': 'IP6SLAVEDNS', 'type': String },
            'ipv6_prefix': { 'name': 'IP6STATICPREFIX', 'type': String },
            'pppoe_proxy': { 'name': 'PPPOEPROXY', 'type': Integer },
            'pppoe_user': { 'name': 'PPPOEUSER', 'type': String },
            'pppoe_password': { 'name': 'PPPOEPASSWD', 'type': String },
            'pppoe_name': { 'name': 'PPPOENAME', 'type': String },
            'pppoe_auth_mode': { 'name': 'PPPOEAUTHMODE', 'type': Integer },
            'pppoe_mode': { 'name': 'PPPOEMODE', 'type': Integer },
            'pppoe_idletime': { 'name': 'PPPOEIDLETIME', 'type': Integer },
            'uport': { 'name': 'UPORT', 'type': Integer },
            'ssid_ports': { 'name': 'SSID', 'type': Integer },
            'vlan_mode': { 'name': 'VLANMODE', 'type': Integer },
            'trans_state': { 'name': 'TRANSSTATE', 'type': Boolean },
            'trans_value': { 'name': 'TRANSVALUE', 'type': Integer },
            'trans_cos': { 'name': 'TRANSCOS', 'type': Integer },
            'qinq_state': { 'name': 'QINQSTATE', 'type': Boolean },
            'tag_protocol_id': { 'name': 'TPID', 'type': Integer },
            'svlan': { 'name': 'SVLAN', 'type': Integer },
            'qinq_cos': { 'name': 'QINQCOS', 'type': Integer },
            'dhcp_remote_id': { 'name': 'DHCPREMOTEID', 'type': String },
            'upnp': { 'name': 'UPNP', 'type': Boolean },
            'activation': { 'name': 'ACTIVATION', 'type': Boolean },
            'gemport': { 'name': 'GEMPORT', 'type': Integer },
        }


class SetONUBandWidthProfile(Command):
    def __init__(
        self,
        olt_id: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        bandwidth: str = None,
        gpon_service_bw:str = None
        ):
        super().__init__('CFG', 'ONUBWPROFILE')
        
        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLTID', IPv4Address(olt_id)),
            pon_id = Parameter('PONID', String(pon_id)),
            pon_id_type = Parameter('ONUIDTYPE', String(onu_id_type)),
            onu_id = Parameter('ONUID', String(onu_id))
        )
        
        data = {}
        
        if bandwidth is not None:
            data['bandwidth'] = Parameter('BW', String(bandwidth))
        if gpon_service_bw is not None:
            data['gpon_service_bw'] = Parameter('GPONSERVICEBW', String(gpon_service_bw))
            
        if len(data) == 0:
            raise AttributeError('Set at least one of the parameters, gpon_service_bw or bandwidth')

        self.payload = ParamBlock(**data)
    

class UnbindONUBandwidthProfile(Command):
    def __init__(
        self,
        olt_id: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        ):
        super().__init__('UNBIND', 'ONUBWPROFILE')

        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLDID', IPv4Address(olt_id)),
            pon_id = Parameter('PONID', String(pon_id)),
            onu_id_type = Parameter('ONUIDTYPE', String(onu_id_type)),
            onu_id = Parameter('ONUID', String(onu_id))
        )


class ConfigLTBandwidthProfile(Command):
    def __init__(
        self,
        olt_id: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        up_bw_profile: str,
        down_bw_profile: str,
        wan_name: str = None,
        wan_index: int = None
        ):
        
        data = {}
        
        
        data.update({
            'up_bw_profile': Parameter('UPBWPROFILE', String(up_bw_profile)),
            'down_bw_profile': Parameter('DOWNBWPROFILE', String(down_bw_profile))
        })
        
        if wan_name:
            data['wan_name'] = Parameter('WANNAME', String(wan_name))
        
        if wan_index:
            data['wan_index'] = Parameter('WANINDEX', String(wan_index))
        
        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLTID', IPv4Address(olt_id)),
            pon_id = Parameter('PONID', String(pon_id)),
            onu_id_type = Parameter('ONUIDTYPE', String(onu_id_type)),
            onu_id = Parameter('ONUID', String(onu_id))
        )
        

class SetPortBindFlowPolicy(Command):
    def __init__(
        self,
        onu_ip: Optional[str] = None,
        olt_id: Optional[str] = None,
        pon_id: Optional[str] = None,
        onu_id_type: Optional[str] = None,
        onu_id: Optional[str] = None,
        ingress_policy: str = None,
        egress_policy: str = None,
        ingress_rule: str = None,
        egress_rule: str = None,
        ):
        super().__init__('CFG', 'PORTBINDFLOWPOLICY')

        access = {}

        if onu_ip:
            access['onu_ip'] = Parameter('ONUIP', IPv4Address(onu_ip))
        elif olt_id and pon_id and onu_id_type and onu_id:
            access['olt_id'] = Parameter('OLTID', IPv4Address(olt_id))
            access['pon_id'] = Parameter('PONID', String(pon_id))
            access['onu_id_type'] = Parameter('ONUIDTYPE', String(onu_id_type))
            access['onu_id'] = Parameter('ONUID', String(onu_id))
        else:
            raise AttributeError('Invalid ONU identification parameters. Please provide either "onu_ip" or a valid combination of "olt_id", "pon_id", "onu_id_type", and "onu_id"')

        if not (ingress_policy and egress_policy):
            raise AttributeError('Need to set Ingress and Egress policy')

        data = {
            'ingress_policy': Parameter('IngressPolicy', String(ingress_policy)),
            'egress_policy': Parameter('EgressPolicy', String(egress_policy))
        }

        if ingress_rule is not None:
            data['ingress_rule'] = Parameter('IngressRule', String(ingress_rule))

        if egress_rule is not None:
            data['egress_rule'] = Parameter('EgressRule', String(egress_rule))

        self.staging.aid = ParamBlock(**access)
        self.payload = ParamBlock(**data)

class SetUplinkTrunk(Command):
    def __init__(
        self, 
        onu_ip: Optional[str] = None,
        olt_id: Optional[str] = None,
        trunk_no: Optional[int] = None,
        master_port: Optional[str] = None,
        member_port: Optional[str] = None
        ):
        super().__init__('SET', 'UPLINKTRUNK')
        access = {}
        
        if onu_ip:
            access['onu_ip'] = Parameter('ONUIP', IPv4Address(onu_ip))
        elif olt_id:
            access['olt_id'] = Parameter('OLTID', IPv4Address(olt_id))
        else:
            raise AttributeError('Invalid Identification. Please enter ONU IP or OLT IP address')
        
        if not (trunk_no and master_port and member_port):
            raise AttributeError("Please enter Trunk Number, Master Port, Member Port")
        
        self.staging.aid = ParamBlock( **access )
        self.payload = ParamBlock(
            trunk_no = Parameter('TRUNKNO', Integer(trunk_no)),
            master_port = Parameter('MASTERPORT', String(master_port)),
            member_port = Parameter('MEMBERPORT', String(member_port))
        )

class ListTrunkInfo(Command):
    def __init__(
        self, 
        onu_ip: Optional[str] = None,
        olt_id: Optional[str] = None,
        ):
        
        super().__init__('LST', 'TRUNKINFO')
        access = {}
        
        if onu_ip:
            access['onu_ip'] = Parameter('ONUIP', IPv4Address(onu_ip))
        elif olt_id:
            access['olt_id'] = Parameter('OLTID', IPv4Address(olt_id))
        else:
            raise AttributeError('Invalid Identification. Please enter ONU IP or OLT IP address')
        
        self.staging.aid = ParamBlock( **access )


class ConfigManageVlan(Command):
    def __init__(
        self,
        onu_ip: Optional[str] = None,
        olt_id: Optional[str] = None,
        pon_id: Optional[str] = None,
        onu_id_type: Optional[str] = None,
        onu_id: Optional[str] = None,
        name: Optional[str] = None,
        port_num: Optional[int] = None,
        vlan_mode: Optional[str] = None,
        svlan: Optional[int] = None,
        cvlan: Optional[int] = None,
        ip: Optional[str] = None,
        mask: Optional[str] = None,
        gateway: Optional[str] = None
        ):
        super().__init__('CFG','MANAGEVLAN')

        access = {}
        data = {}

        if onu_ip:
            access['onu_ip'] = Parameter('ONUIP', IPv4Address(onu_ip))
        elif olt_id and pon_id and onu_id_type and onu_id:
            access['olt_id'] = Parameter('OLTID', IPv4Address(olt_id))
            access['pon_id'] = Parameter('PONID', String(pon_id))
            access['onu_id_type'] = Parameter('ONUIDTYPE', String(onu_id_type))
            access['onu_id'] = Parameter('ONUID', String(onu_id))
        else:
            raise AttributeError('Invalid ONU identification parameters. Please provide either "onu_ip" or a valid combination of "olt_id", "pon_id", "onu_id_type", and "onu_id"')

        if port_num is not None:
            data['portno'] = Parameter('PORTNO', Integer(port_num))

        if not (name and vlan_mode, svlan, cvlan, ip, mask, gateway):
            raise ArithmeticError('Please set Name, Vlan Mode, SVlan, CVlan, IP address, mask and gateway')

        data.update({
            'name': Parameter('NAME', String(name)),
            'vlan_mode': Parameter('VLANMODE', Integer(vlan_mode)),
            'svlan': Parameter('SVLAN', Integer(svlan)),
            'cvlan': Parameter('CVLAN', Integer(cvlan)),
            'ip': Parameter('IP', IPv4Address(ip)),
            'mask': Parameter('MASK', IPv4Address(mask)),
            'gateway': Parameter('GATEWAY', IPv4Address(gateway))
        })

        self.staging.aid = ParamBlock(**access)
        self.payload = ParamBlock(**data)

class ListManageVlan(Command):
    def __init__(
        self,
        olt_id: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        ):
        super().__init__('LST', 'MANAGEVLAN')

        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLDID', IPv4Address(olt_id)),
            pon_id = Parameter('PONID', String(pon_id)),
            onu_id_type = Parameter('ONUIDTYPE', String(onu_id_type)),
            onu_id = Parameter('ONUID', String(onu_id))
        )


class ActivateONU(Command):
    def __init__(
        self,
        olt_id: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        ):
        super().__init__('ACT', 'ONU')

        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLDID', IPv4Address(olt_id)),
            pon_id = Parameter('PONID', String(pon_id)),
            onu_id_type = Parameter('ONUIDTYPE', String(onu_id_type)),
            onu_id = Parameter('ONUID', String(onu_id))
        )


class DeactivateONU(Command):
    def __init__(
        self,
        olt_id: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        ):
        super().__init__('DEACT', 'ONU')

        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLDID', IPv4Address(olt_id)),
            pon_id = Parameter('PONID', String(pon_id)),
            onu_id_type = Parameter('ONUIDTYPE', String(onu_id_type)),
            onu_id = Parameter('ONUID', String(onu_id))
        )
        

class SetONUSwitch(Command):
    def __init__(
        self,
        olt_id: str,
        pon_id: str,
        onu_id_type: str,
        onu_id: str,
        switch:bool
        ):
        super().__init__('SET', 'ONUSWITCH')

        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLDID', IPv4Address(olt_id)),
            pon_id = Parameter('PONID', String(pon_id)),
            onu_id_type = Parameter('ONUIDTYPE', String(onu_id_type)),
            onu_id = Parameter('ONUID', String(onu_id))
        )

        self.payload = ParamBlock(
            switch = Parameter('ONUSWITCH', Boolean(switch))
        )


class ResetBoard(Command):
    def __init__(
        self,
        olt_id: str,
        boardid: str
    ):
        super().__init__('RST', 'BOARD')

        self.staging.aid = ParamBlock(
            olt_id = Parameter('OLTID', IPv4Address(olt_id)),
            boardid = Parameter('BOARDID', String(boardid))
        )

