Python-MRPC
===========

A Python remote procedure call framework that will work in mesh networks, and is meant for IoT applications.

Install using pip:

```
pip install mrpc
```

# Example Usage

Python MRPC allows programmers to create powerful client/server programs with very little code.
Here's an example of a server and client:

## Server

```python
import mrpc

MRPC = mrpc.MRPC()

@MRPC.service
def light(arg):
    if type(arg) is bool:
        return arg
    return False

if __name__ == "__main__":
    MRPC.run()
```

## Client

```python
import mrpc

MRPC = mrpc.MRPC(host = "127.0.0.1")

light = MRPC.Proxy("*.light")
print(light(True).get())
```
