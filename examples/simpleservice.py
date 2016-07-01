#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

class SimpleService(mrpc.Service):
    @mrpc.service.method
    def echo(self, msg):
        return msg

class LivingRoom(mrpc.Service):
    @mrpc.service.method
    def temperature(self, temp):
        print("Temperature:", temp)

if __name__ == "__main__":
    mrpc.use_transport(SocketTransport(host = "192.168.1.4"))
    mrpc.register_service(SimpleService())
    mrpc.register_service(LivingRoom())
    mrpc.LocalNode.run()
