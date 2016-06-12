import struct
import json
import exception
import socket

def from_bytes(raw_bytes):
    try:
        obj = json.loads(raw_bytes)
        if Response.json_obj_is(obj):
            return Response.from_json(obj)
        if Request.json_obj_is(obj):
            return Request.from_json(obj)
    except:
        return None

class Message(object):
    required_fields = ["id", "src", "dst"]
    def __init__(self, **kwargs):
        self.obj = dict(kwargs)

    @property
    def bytes(self):
        return json.dumps(self.obj)

    def copy(self):
        copy = Message()
        copy.obj = json.loads(self.bytes)
        return copy

    def __str__(self):
        return json.dumps(self.obj)

    def __getattr__(self, name):
        if not name in self.obj:
            AttributeError
        return self.obj[name]

    def __setattr__(self, name, value):
        if name == "obj": object.__setattr__(self, name, value)
        else: self.obj[name] = value

class Request(Message):
    required_fields = Message.required_fields + ["procedure"]
    @staticmethod
    def json_obj_is(json_obj):
        return all([field in json_obj for field in Request.required_fields])
    @staticmethod
    def from_json(json_obj):
        if not Request.json_obj_is(json_obj):
            raise exception.InvalidReqeust("Message is not a request")
        request = Request(**json_obj)
        return request

class Response(Message):
    required_fields = Message.required_fields
    @staticmethod
    def json_obj_is(json_obj):
        return all([field in json_obj for field in Response.required_fields]) and ("result" in json_obj or "error" in json_obj)
    @staticmethod
    def from_json(json_obj):
        if not Response.json_obj_is(json_obj):
            raise exception.ParseError("Message is not a response")
        response = Response(**json_obj)
        if "error" in json_obj: response.error = json_obj["error"]
        elif "result" in json_obj: response.result = json_obj["result"]
        else: raise exception.ClientError("Reponse object does not contain error or result")
        return response
