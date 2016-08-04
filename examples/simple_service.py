#!/usr/bin/python
import mrpc

MRPC = mrpc.MRPC()

@MRPC.service
def temperature():
    return 24

@MRPC.service
def light(arg):
    if type(arg) is bool:
        return arg
    return False

if __name__ == "__main__":
    MRPC.run()
