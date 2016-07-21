#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

MRPC = mrpc.MRPC()
MRPC.use_transport(SocketTransport(0, "192.168.1.4"))
server = MRPC.Proxy("*")
print(server.light(True).get())

