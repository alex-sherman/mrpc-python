#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

MRPC = mrpc.MRPC()

@MRPC.service
def temperature(temp):
    print("Temperature:", temp)

if __name__ == "__main__":
    MRPC.use_transport(SocketTransport(host = "192.168.1.4"))
    MRPC.run()
