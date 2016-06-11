#!/usr/bin/python
import mrpc
from mrpc.transport import SocketTransport

mrpc.use_transport(SocketTransport(50020))
server = mrpc.Proxy(mrpc.Path.BROADCAST)
print server.Reflect().get()
