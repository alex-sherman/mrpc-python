#!/usr/bin/python
import mrpc
from mrpc.transport import SocketTransport

class SimpleService(mrpc.Service):
    @mrpc.service.method
    def echo(self, msg):
        return msg

class OtherService(mrpc.Service):
    @mrpc.service.method
    def echo(self, msg):
        return msg + "OTHER"

if __name__ == "__main__":
    mrpc.use_transport(SocketTransport())
    mrpc.register_service(SimpleService())
    mrpc.register_service(OtherService())
    mrpc.LocalNode.run()
