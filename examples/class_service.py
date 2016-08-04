#!/usr/bin/python
from __future__ import print_function
import mrpc
from mrpc.transport import SocketTransport

MRPC = mrpc.MRPC()

class HomeAutomation(object):
    __metaclass__ = MRPC.ServiceType
    def __init__(self):
        self.light_value = False
        self.last_temp = 24

    def light(self, arg):
        if type(arg) is bool:
            self.light_value = arg
        return self.light_value

    def temperature(self):
        self.last_temp += 1
        return self.last_temp

if __name__ == "__main__":
    MRPC.run()
