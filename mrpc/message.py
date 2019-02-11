import struct
import json
from . import exception
import socket

class Message(object):
    required_fields = ["id", "src", "dst"]
    def __init__(self, **kwargs):
        self.obj = dict(kwargs)

    @staticmethod
    def from_bytes(raw_bytes):
        obj = json.loads(raw_bytes)
        return Message(**obj)

    @property
    def is_valid(self):
        return all([field in self.obj for field in Message.required_fields])

    @property
    def is_request(self):
        return self.is_valid and not self.is_response
    
    @property
    def is_response(self):
        return self.is_valid and ("result" in self.obj or "error" in self.obj)
    
    @property
    def bytes(self):
        return json.dumps(self.obj).encode("ascii")
    def copy(self):
        copy = Message()
        copy.obj = json.loads(self.bytes)
        return copy

    def __str__(self):
        return json.dumps(self.obj)

    def __getattr__(self, name):
        if name not in self.obj:
            raise AttributeError
        return self.obj[name]

    def __setattr__(self, name, value):
        if name == "obj": object.__setattr__(self, name, value)
        else: self.obj[name] = value
