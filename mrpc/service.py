import threading
import socket
import logging
import time
import exception
import json
import message
import inspect
import types
import reflection
from reflection import RPCType

def method(*args, **kwargs):
    if(len(args) > 0 and isinstance(args[0], types.FunctionType)):
        args[0].options = kwargs
        args[0].jrpc_method = True
        argSpec = inspect.getargspec(args[0])
        defaults = len(argSpec[3]) if argSpec[3] != None else 0
        argNames = argSpec[0][1:]
        argTypes = args[1:] if len(args) > 1 else []
        argCount = len(argNames)
        while len(argTypes) < len(argNames):
            argTypes.append(reflection.UNKNOWN())
        #Mark any parameters with defaults as optional
        if defaults > 0:
            for optionalArg in argTypes[-defaults:]:
                optionalArg.optional = True
        args[0].arguments = zip(argNames, argTypes)
        return args[0]
    return lambda func: method(func, *args, **kwargs)

class rpc_property(property):
    def __init__(self, getter):
        property.__init__(self, getter)
        jrpc_object.__init__(self)

class Service(object):
    def __init__(self):
        self.transports = []

    def _methods(self):
        return dict([method for method in inspect.getmembers(self) if hasattr(method[1], "jrpc_method") and method[1].jrpc_method])

    def get_method(self, method):
        methods = self._methods()
        if method in methods:
            return methods[method]
        return None
