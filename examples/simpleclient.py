#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

mrpc.use_transport(SocketTransport(50020))
server = mrpc.Proxy("/SimpleService")
print(server.echo("Faff").get())
server = mrpc.Proxy("/OtherService")
print(server.echo("Faff").get())

