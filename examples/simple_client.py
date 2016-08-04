#!/usr/bin/python
import mrpc

MRPC = mrpc.MRPC(host = "127.0.0.1")

temperature = MRPC.Proxy("*.temperature")
print(temperature().get())

light = MRPC.Proxy("*.light")
print(light(not light().get()).get())
