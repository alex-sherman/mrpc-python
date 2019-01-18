import threading
import socket
import logging
import time
from . import exception
import json
from . import message
import inspect
import types
from functools import wraps

def valid_args(func, *args, **kwargs):
    try:
        inspect.getcallargs(func, *args, **kwargs)
        return True
    except Exception as e:
        return False

def Service(mrpc):
    class service(object):
        def __init__(self, func, service_name = None):
            self.aliases = []
            @wraps(func)
            def wrapped(value):
                args = [value]
                kwargs = {}
                if value is None and valid_args(func):
                    args = []
                elif type(value) is list and valid_args(func, *value):
                    args = value
                elif type(value) is dict and valid_args(func, **value):
                    args = []
                    kwargs = value
                return func(*args, **kwargs)
            self.wrapped = wrapped
            mrpc.services[service_name if service_name else func.__name__] = self
        def __call__(self, value):
            return self.wrapped(value)
        def respond(self, name):
            if name not in self.aliases:
                self.aliases.append(name)
            return self
        def close(self):
            pass
    return service

def create_service_type(mrpc):
    class ServiceType(type):
        def __init__(cls, name, bases, dct):
            type.__init__(cls, name, bases, dct)
            cls.single = cls.__new__(cls, name, bases, dct)
            cls.__init__(cls.single)
            methods = dict([(method[0], type(method[1])) for method in inspect.getmembers(cls.single) if type(method[1]) is types.MethodType and method[0][0] != "_"])
            for method_name, method in methods.items():
                mrpc.service(getattr(cls.single, method_name))

    return ServiceType
