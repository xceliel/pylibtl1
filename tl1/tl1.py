from typing import Union

from .session import Session
from .base import Command
from .base import parse_response
from .base import Response
from .base import AutonomousMessage
from .base import AcknowledgmentMessage

class TL1:

    def __init__(self, host:str = None, port:int = 0, vendor = None,  timeout:int = 5):
        self.session = Session(host, port, timeout)
        self.connected = False
        self.vendor = vendor()

        if self.session.sock is not None:
            self.connected = True

    def execute(self, cmd:Command = None) -> Union[
        Response,
        AutonomousMessage,
        AcknowledgmentMessage
    ]:
        """
            Execute TL1 command and return response

        Args:
            cmd (Command, optional): TL1 Command. Defaults to None.

        Raises:
            ConnectionError: If session is not connected it's raised a error

        Returns:
            Union[ Response, AutonomousMessage, AcknowledgmentMessage ]: Response
        """
        if not self.connected:
            raise ConnectionError('Session is not connected')

        if not isinstance(cmd, Command):
            return None

        self.session.write(str(cmd))

        return parse_response(self.session.get_response(), cmd.modifiers, self.vendor)

    def close(self) -> bool:
        """
            Close the TL1 session

        Returns:
            bool: Check if it was sucessfully closed
        """
        if self.connected:
            self.session.close()
            self.session = None

            return True
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
