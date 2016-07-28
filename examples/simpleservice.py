#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

MRPC = mrpc.MRPC()

error = 0

@MRPC.service
def temperature(temp):
    global error
    error += 1
    if error % 2:
        raise mrpc.NoReturn
    print("Temperature:", error)
    return error

if __name__ == "__main__":
    MRPC.use_transport(SocketTransport())
    MRPC.run()
