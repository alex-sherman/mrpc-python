#!/usr/bin/python
from __future__ import print_function
import mrpc
import time

MRPC = mrpc.MRPC(broadcast = "192.168.1.255")

# RPC style
print(MRPC.rpc("LivingRoom.relay").get())
print(MRPC.srpc("LivingRoom.relay")) # Alias to call .get()

# Async RPC style
MRPC.rpc("LivingRoom.relay").when(lambda value: print(value))

# Proxy style
LivingRoom = MRPC.Proxy("LivingRoom")
print(LivingRoom.relay().get())

# Async proxy style
LivingRoom.relay().when(lambda value: print(value))

# Argument conversions
LED = MRPC.Proxy("LED")
LED.color(255, 255, 255)                # Same as LED.color([255, 255, 255])
LED.color(r = 255, g = 255, b = 255)    # Same as LED.color({r: 255, g: 255, b: 255})