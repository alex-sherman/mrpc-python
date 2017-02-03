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

## Constructing and Destructing an MRPC node
To use MRPC, we have to construct an MRPC node which will handle communication. This construction opens a UDP socket and starts a thread to listen for incoming data. If your application wishes to dispose of the MRPC node, it **must** call `.close()` in order to close the UDP socket and stop the listener thread.
```python
import mrpc

# Specify broadcast address, otherwise defaults to 255.255.255.255
MRPC = mrpc.MRPC(broadcast = "192.168.1.255")

# Don't forget to dispose if you finish with the node!
MRPC.close()
```

## Using `MRPC.rpc()` to invoke remote services
The first and most robust way to invoke remote services is using `.rpc()`. This function returns an `RPCRequest` object immediately without blocking. One way to retrieve the result is to call `.get()` which will block and return the **first** response that is received. A convenience method `.srpc()` is the same as calling `.get()` on the result of `.rpc()`.
```python
MRPC.rpc("LED.color", [255, 255, 255]).get()  # Must call blocking .get() to retrieve result
MRPC.srpc("LED.color", [255, 255, 255])       # Synchronous rpc, alias to call .get()
```
The RPCRequest object that `.rpc()` returns, can also be used to attach a call back. The call back will be called **each** time a response is received for the request and is executed in a **different thread** than the main thread.
```python
MRPC.rpc("Thermometer.temperature").when(lambda value: print(value))
```
## Using Proxies to invoke remote services
It may be convenient when invoking services on a specific path name many times, to wrap the name as a Proxy. For instance if we wish to toggle the lights in the LivingRoom, we might wrap the LivingRoom path as an object and make multiple calls to the light service. 
```python
LivingRoom = MRPC.Proxy("LivingRoom")
```
First we check the current value of the lights by calling the service without any arguments.
```python
light_value = LivingRoom.lights().get()
```
Then we can call the service again with the negated value to toggle the lights.
```python
LivingRoom.lights(not light_value).get()
```
Because proxies also return `RPCRequests` we need to call `.get()` or use `.when()` in order to retrieve the response values.
```python
LivingRoom.temperature().when(lambda value: print(value))
```
## Argument conversions in Proxies
MRPC services can only accept a single value as their argument, but sometimes we may want to use multiple arguments in our invocations. The convention for multiple arguments in MRPC is to pass them as either an array or object. Proxies will automatically convert multiple arguments to an array or object. The multiple arguments must either be all unnamed, or named, and never mix the two invocation styles.
```python
LED = MRPC.Proxy("LED")
LED.color(255, 255, 255)          # Same as LED.color([255, 255, 255])
LED.color(r=255, g=255, b=255)    # Same as LED.color({r: 255, g: 255, b: 255})
```
