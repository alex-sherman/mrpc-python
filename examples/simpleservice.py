#!/usr/bin/python
import jrpc
from jrpc.transport import SocketTransport

class SimpleService(jrpc.service.RemoteObject):
    @jrpc.service.method
    def echo(self, msg):
        return msg

if __name__ == "__main__":
    server = SimpleService()
    transport = SocketTransport(50021)
    transport.add_service(server)
    transport.thread.join()
