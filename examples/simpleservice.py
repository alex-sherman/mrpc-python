#!/usr/bin/python
import mrpc
from mrpc.transport import SocketTransport

class SimpleService(mrpc.Service):
    @mrpc.service.method
    def echo(self, msg):
        return msg

if __name__ == "__main__":
    server = SimpleService()
    mrpc.use_transport(SocketTransport())
    mrpc.set_service(server)
    mrpc.LocalNode.run()
