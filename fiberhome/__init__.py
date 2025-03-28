from tl1.base import VendorBase
from tl1.base import AcknowledgmentMessage
from tl1.base import AutonomousMessage

from .objects import Response

class Fiberhome(VendorBase):
    acknowledgement = AcknowledgmentMessage
    autonomous = AutonomousMessage
    response = Response