"""
Modules used in the implementation:

- `socket`: Provides methods for network connections, including `recv` and `fileno`.
- `selectors`: Used for the `DefaultSelector` class, which provides efficient I/O multiplexing.
- `time`: Provides the `time` method for handling time-related operations.
"""

import socket
import selectors
import time

# Some special characters for Telnet
IAC     = bytes([255]) # IAC (Interpret As Command) - To indicates a Telnet command
DONT    = bytes([254]) # Instruct other party to not use a protocol mechanism
DO      = bytes([253]) # Instruct other party to use a protocol mechanism
WONT    = bytes([252]) # Informs other party that this party will not use a protocol mechanism
WILL    = bytes([251]) # Informs other party that this party will use a protocol mechanism
SB      = bytes([250]) # Initiate the negotiation of a sub-service of a protocol mechanism
SE      = bytes([240]) # End of negotiation (or data block) of a sub-service of a protocol mechanism
theNULL = bytes([0])   # The null character, generally indicanting the end of a string

class Session:
    """
    A reimplementation of the `telnetlib` module with enhanced features and improvements.

    Notable Improvements:
    - Context Management Support: The session can be used within a `with` statement 
                                    for more convenient and reliable session handling.
    - Enhanced Response Handling: The `get_response` method now waits up to 5 seconds 
                                for incoming data. If no data is received within this time frame, 
                                an error is raised.

    This class is designed to provide a more user-friendly, reliable
    and feature-rich interface for interacting with remote systems over Telnet.
    """

    def __init__(self, host:str = None, port:int = None, timeout:int = 5):
        """
        Initialize a session instance. If no parameters are provided, 
        they can be set later using the `connect` method.

        Args:
            host (str, optional): The IP address or hostname of the remote host. Defaults to None.
            port (int, optional): The port number to use for the connection. Defaults to None.
            timeout (int, optional): The time to wait for the connection to be established in sec. 
                                        Defaults to 5.
        """
        self.eof = False
        self.sock = None
        self.host = host
        self.port = port
        self.timeout = timeout

        if all([host, port]):
            self.connect(host, port, timeout)

    def connect(self, host:str = None, port:int = None, timeout:int = 5):
        """
        Attempt to establish a connection with a remote host using a telnet session.

        If no parameters are provided, the method will use the default values
        from the session instance.

        Args:
            host (str, optional): The IP address or hostname of the remote host to connect to. 
                                    Defaults to None.

            port (int, optional): The port number to use for the connection. 
                                    Defaults to None.

            timeout (int, optional): The time to wait for the connection to be established in sec. 
                                    Defaults to 5.

        Raises:
            ConnectionError: If there is an ongoing session, if the session could not be started, 
                                or if no valid parameters are provided.

        Returns:
            bool: True if the connection is successfully established, False otherwise.
        """
        self.host = host or self.host
        self.port = port or self.port
        self.timeout = timeout or self.timeout

        if not all([host, port]):
            raise ConnectionError("No host ip and port were set")

        # Lets avoid problems
        if self.sock is not None:
            raise ConnectionError("Close the current session before starting a new one")

        self.sock = socket.create_connection((self.host, self.port), self.timeout)

        # In case it doesn't throw error
        if self.sock is None:
            raise ConnectionError("Couln't start new session")

        return True

    def fileno(self):
        """
            Get socket file number

        Returns:
            int: file number
        """
        return self.sock.fileno()

    def write(self, buffer:str):
        """
            Send data to other party
            but its encode to ascii before trying

        Args:
            buffer (str): Data to send to the other party
        """
        parsed = buffer.encode('ascii')
        if IAC in parsed:
            parsed = parsed.replace(IAC, IAC+IAC)
        self.sock.sendall(parsed)

    def get_content(self):
        """
            Check if theres data in the socket and 
            return all its data until theres no data
            available

        Returns:
            bytes: Data found in network socket
        """
        buf = b''
        while self.sock_avail():
            buf = buf + self.sock.recv(50)

        return buf.decode('ascii')

    def get_response(self, timeout:int = 5):
        """
            Get data from data socket

        Args:
            timeout (int, optional): Maximum timeout to find data. Defaults to 5.

        Raises:
            EOFError: Indicating the timeout exceeded and didn't found any data

        Returns:
            bytes: returned data
        """
        start = time.time()
        end = time.time()

        while (end-start) < timeout:

            if self.sock_avail():
                return self.get_content()

            end = time.time()

        raise EOFError("Didnt found any response")

    def sock_avail(self):
        """
            Checks if theres data available in the network socket

        Returns:
            bool: value indicating if theres data available
        """
        with selectors.DefaultSelector() as selector:
            selector.register(self.sock, selectors.EVENT_READ)
            return bool(selector.select(0))

    def close(self):
        """
            Close the telnet session
        """
        sock = self.sock
        self.sock = None
        self.eof = True
        if sock:
            sock.close()

    def __enter__(self):
        """
        Initialize the context for the 'with' statement.

        This method is called when entering the 'with' block and returns the class instance
        to be used within the block.

        Returns:
            self: The current class instance, allowing access within the 'with' block.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up when exiting the 'with' statement.

        This method is called when exiting the 'with' block, whether an exception was raised
        or not. It handles the cleanup by closing the resource.

        Args:
            exc_type (type): The exception class (if any) raised in the 'with' block.
            exc_val (Exception): The exception instance (if any) raised in the 'with' block.
            exc_tb (traceback): The traceback object (if any) for the raised exception.
        """
        self.close()
