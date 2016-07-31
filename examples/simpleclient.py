#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport
import time

MRPC = mrpc.MRPC()
MRPC.use_transport(SocketTransport(host = "192.168.1.4"))
light = MRPC.Proxy("*.light")
light(not light().get())
#uuid = MRPC.Proxy("*.uuid")
#uuid().when(lambda value: print(value)).wait()
#time.sleep(5)

