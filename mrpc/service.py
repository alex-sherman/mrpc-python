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
from functools import wraps

def valid_args(func, instance, *args, **kwargs):
    try:
        if instance:
            inspect.getcallargs(func, instance, *args, **kwargs)
        else:
            inspect.getcallargs(func, *args, **kwargs)
        return True
    except Exception as e:
        print(e)
        return False


class method(object):
    def __init__(self, func):
        @wraps(func)
        def wrapped(value, instance = None):
            args = [value]
            kwargs = {}
            if value is None and valid_args(func, instance):
                args = []
            elif type(value) is list and valid_args(func, instance, *value):
                args = value
            elif type(value) is dict and valid_args(func, instance, **value):
                args = []
                kwargs = value
            if instance:
                return func(instance, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        self.wrapped = wrapped
    def __get__(self, instance, owner):
        output = lambda value: self.wrapped(value, instance)
        output.mrpc_method = True
        return output
    def __call__(self, value):
        return self.wrapped(value)

class rpc_property(property):
    def __init__(self, getter):
        property.__init__(self, getter)
        jrpc_object.__init__(self)

class Service(object):
    def __init__(self):
        self._methods = dict([_method for _method in inspect.getmembers(self) if hasattr(_method[1], "mrpc_method") and _method[1].mrpc_method])

    def get_method(self, method):
        if method in self._methods:
            return self._methods[method]
        return None
