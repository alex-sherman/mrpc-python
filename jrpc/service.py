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

class RemoteObject(object):
    def __init__(self):
        self.transports = []
    def _get_methods(self):
        return dict([method for method in inspect.getmembers(self) if hasattr(method[1], "jrpc_method") and method[1].jrpc_method])
    def _get_objects(self):
        return dict([obj for obj in inspect.getmembers(self) if isinstance(obj[1], RemoteObject)])

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

    def on_receive(self, message):
        method = self.get_method(message.method)
        if not method is None:
            return method(message.params)
        raise JRPCError("Method not found")

class CallBack(object):
    def __init__(self, procedure_name, proxy):
        self.proxy = proxy
        self.procedure_name = procedure_name
    def __getattr__(self, name):
        return CallBack(self.procedure_name + "." + name, self.proxy)
    def __call__(self, *args, **kwargs):
        return self.proxy.rpc(self.procedure_name, args, kwargs)

class SocketProxy(object):
    def __init__(self, port, host = 'localhost', socktype = socket.SOCK_STREAM, timeout = 1):
        socket.setdefaulttimeout(timeout)
        self.socket = None
        self.next_id = 1
        self.lock = threading.Lock()
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socktype)
        try:
            self.socket.connect((host, port))
        except socket.error as e:
            if e.args[0] != 111:
                raise exception.JRPCError("An error occured", e)

    def rpc(self, remote_procedure, args, kwargs):
        self.lock.acquire()
        try:
            msg = message.Request(self.next_id, remote_procedure, [args, kwargs])
            self.next_id += 1

            # Attempt sending and connection if neccessary
            try:
                msg.serialize(self.socket)
            except socket.error as e:
                # Connection error, try to connect and send
                if e.args[0] == 32:
                    try:
                        self.socket.connect((self.host, self.port))
                        msg.serialize(self.socket)
                    except socket.error as e:
                        raise exception.JRPCError("Unable to connect to remote service", e)
                else: raise e

            response = message.deserialize(self.socket)
            if not type(response) is message.Response:
                raise exception.JRPCError("Received a message of uknown type")
            if response.id != msg.id: raise exception.JRPCError(0, "Got a response for a different request ID")
            if hasattr(response, "result"):
                return response.result
            elif hasattr(response, "error"):
                raise exception.JRPCError.from_error(response.error)
            raise Exception("Deserialization failure!!")
        finally:
            self.lock.release()

    def close(self):
        if "socket" in self.__dict__ and self.socket != None:
            self.socket.close()
        self.socket = None
        
    def __del__(self):
        self.close()
        del self
        
    def __getattr__(self, name):
        return CallBack(name, self)
