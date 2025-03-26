import sys, socket, selectors, time


# Some special characters for Telnet
IAC     = bytes([255]) # IAC (Interpret As Command) - This indicates that the following bytes represent a Telnet command
DONT    = bytes([254]) # Instruct other party to not use a protocol mechanism
DO      = bytes([253]) # Instruct other party to use a protocol mechanism
WONT    = bytes([252]) # Informs other party that this party will not use a protocol mechanism 
WILL    = bytes([251]) # Informs other party that this party will use a protocol mechanism 
SB      = bytes([250]) # Initiate the negotiation of a sub-service of a protocol mechanism
SE      = bytes([240]) # End of negotiation (or data block) of a sub-service of a protocol mechanism 
theNULL = bytes([0])   # The null character, generally indicanting the end of a string


class Session:
    """
    A reimplementation of the telnetlib module with additional features and enhancements.

    Improvements:
    - Support for context management using 'with' statements, allowing for more convenient and reliable session handling.
    - Enhanced response handling in the `get_response` method, which waits up to 5 seconds for data. If no data is received within this time frame, an error is raised.

    This class aims to provide a more user-friendly and robust interface for interacting with remote systems over Telnet.
    """
    
    def __init__(self, host:str = None, port:int = None, timeout:int = 5):
        self.sock = None
        self.host = host
        self.port = port
        self.timeout = timeout
        
        if all([host, port]):
            self.connect(host, port, timeout)
        
    def connect(self, host:str = None, port:int = None, timeout:int = 5):
        
        self.host = host or self.host
        self.port = port or self.port
        self.timeout = timeout or self.timeout
        
        # Lets avoid problems
        if self.sock != None:
            raise ConnectionError("Close the current session before starting a new one")
        
        self.sock = socket.create_connection((self.host, self.port), self.timeout)        
        
        # In case it doesn't throw error
        if self.sock == None:
            raise ConnectionError("Couln't start new session")
        
        return True
    
    def fileno(self):
        return self.sock.fileno()
    
    def write(self, buffer:str):
        parsed = buffer.encode('ascii')
        if IAC in parsed:
            parsed = parsed.replace(IAC, IAC+IAC)
        self.sock.sendall(parsed)
    
    def get_content(self):    
        buf = b''
        while self.sock_avail():
            buf = buf + self.sock.recv(50)
            
        return buf    
    
    def get_response(self, timeout:int = 5):
        
        start = time.time()
        end = time.time()
        
        while (end-start) < timeout:
            
            if self.sock_avail():
                return self.get_content()
            
            end = time.time()
            
        raise EOFError("Didnt found any response") 
    
    def sock_avail(self):
        with selectors.DefaultSelector() as selector:
            selector.register(self.sock, selectors.EVENT_READ)
            return bool(selector.select(0))
        
    def close(self):
        sock = self.sock
        self.sock = None
        self.eof = True
        if sock:
            sock.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
