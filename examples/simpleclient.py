#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

mrpc.use_transport(SocketTransport(0, "192.168.1.4"))
server = mrpc.Proxy("/SimpleService")
print(server.echo("faff").get())
print(server.echo("Faff").get())
server = mrpc.Proxy("/OtherService")

