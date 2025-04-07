# Its a bit shitty, but i'll fix it
# ...someday in the distant future
# If you can shit a better lib, please do

from tl1.base import VendorBase
from tl1.base import AcknowledgmentMessage
from tl1.base import AutonomousMessage

from .objects import Response

class Fiberhome(VendorBase):
    acknowledgement = AcknowledgmentMessage
    autonomous = AutonomousMessage
    response = Response
    
