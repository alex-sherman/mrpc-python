Python-MRPC
===========

A Python implementation of the remote procedure call framework MRPC which works in mesh networks, and is meant for IoT applications.
MRPC allows easy communication between a wide variety of devices, more information about MRPC and what languages and platforms it supports [can be found here](https://github.com/alex-sherman/MRPC#mrpc).

Install using pip:

```
pip install mrpc
```

# Example Usage

The Python implementation of MRPC has several nice extensions because of the flexibility of Python.
Below are some examples of extra features available in the Python version of MRPC.

```python
import mrpc

# Specify broadcast address, otherwise defaults to 255.255.255.255
MRPC = mrpc.MRPC(broadcast = "192.168.1.255")

# RPC style
MRPC.rpc("LivingRoom.relay").get()  # Must call blocking .get() to retrieve result
MRPC.srpc("LivingRoom.relay")       # Synchronous rpc, alias to call .get()

# Async RPC style
MRPC.rpc("LivingRoom.relay").when(lambda value: print(value))

# Proxy style
LivingRoom = MRPC.Proxy("LivingRoom")
LivingRoom.relay().get()

# Async proxy style
LivingRoom.relay().when(lambda value: print(value))

# Argument conversions
LED = MRPC.Proxy("LED")
LED.color(255, 255, 255)                # Same as LED.color([255, 255, 255])
LED.color(r = 255, g = 255, b = 255)    # Same as LED.color({r: 255, g: 255, b: 255})
```
