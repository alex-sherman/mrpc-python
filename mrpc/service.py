import threading
import socket
import logging
import time
import exception
import json
import message
import inspect
import types
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

def Service(mrpc):
    class service(object):
        def __init__(self, func, service_name = None):
            self.aliases = []
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
