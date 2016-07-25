#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

MRPC = mrpc.MRPC()
MRPC.use_transport(SocketTransport(host = "10.42.0.39"))
server = MRPC.Proxy("/Faff")
print(server.faff("temperature", {"name": "faff", "aliases": ["Office"]}).get())

