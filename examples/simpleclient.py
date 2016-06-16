#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

mrpc.use_transport(SocketTransport(0, "192.168.1.4"))
server = mrpc.Proxy("*/Routing")
print(server.list_procedures("/Routing").get())

