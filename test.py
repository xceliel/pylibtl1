from commands import DeleteONU
from objects import ONU

o = ONU(1,2,1)
o.id.value = 1
d = DeleteONU(o)

print(d)

