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
    def _get_methods(self):
        return dict([method for method in inspect.getmembers(self) if hasattr(method[1], "jrpc_method") and method[1].jrpc_method])
    def _get_objects(self):
        return dict([obj for obj in inspect.getmembers(self) if isinstance(obj[1], Service)])

    def get_method(self, path):
        methods = self._get_methods()
        if path[0] in methods:
            return methods[path[0]]
        objects = self._get_objects()
        if len(path) > 1 and path[0] in objects:
            return objects[path[0]].get_method(path[1:])
        return None

    @method
    def Reflect(self, types = {}):
        """Reflect returns optional information about
        the remote object's endpoints. The author may not
        specify any reflection information, in which case,
        this will return mostly empty. If specified, this
        method will return custom types, method signatures
        and sub object reflection information
        """
        types = dict(types)
        selfTypes = {}
        methods = {}
        for name, method in self._get_methods().iteritems():
            methods[name] = {'options': method.options, 'arguments': RPCType.ToDict(method.arguments)}
            selfTypes.update(RPCType.ToTypeDef(method.arguments, types))

        interfaces = dict([(name, obj.Reflect(types)) for name, obj in self._get_objects().iteritems()])
        return {
            "types": selfTypes,
            "methods": methods,
            "interfaces": interfaces
        }

