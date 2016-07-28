#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

MRPC = mrpc.MRPC()
MRPC.use_transport(SocketTransport(host = "10.42.0.39"))
temperature = MRPC.Proxy("*.temperature")
ts = [temperature("herp") for _ in range(4)]
print(ts)
print([t.get(throw = False) for t in ts])

