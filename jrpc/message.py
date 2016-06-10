import struct
import json
import exception
import socket

def deserialize(s):
    if s.type == socket.SOCK_STREAM:
        return __deserializeTCP(s)
    if s.type == socket.SOCK_DGRAM:
        return __deserializeUDP(s)

def __deserializeTCP(s):
    buf = s.recv(4)
    if not buf: raise exception.ClientError("Client disconnected")
    size, = struct.unpack("I", buf)
    size = socket.ntohl(size)
    try:
        json_str = ""
        while len(json_str) < size:
            json_str += s.recv(size - len(json_str))
    except socket.timeout:
        raise exception.ClientError("Timeout receiving message")
    return fromjson(json_str)

def __deserializeUDP(s):
    buf = s.recv(1500)
    if not buf: raise exception.ClientError("Client disconnected")
    size, = struct.unpack("!I", buf[:4])
    size = socket.ntohl(size)
    return fromjson(buf[4:size+4])

def fromjson(json_str):
    json_obj = None
    try:
        json_obj = json.loads(json_str)
    except:
        raise exception.ParseError("Invalid json in message: "+json_str)
    
    if Request.json_obj_is(json_obj):
        return Request.from_json(json_obj)
    elif Response.json_obj_is(json_obj):
        return Response.from_json(json_obj)
    return Message(json_obj)

def fromdata(buf):
    size, = struct.unpack("!I", buf[:4])
    return fromjson(buf[4:size+4])

class Message(object):
    def __init__(self, obj = None):
        self.obj = obj
        
    def serialize(self, s):
        s.sendall(self.todata())

    def todata(self):
        json_str = json.dumps(self.obj)
        size = len(json_str)
        return struct.pack("!I{0}s".format(size), size, json_str)

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
    required_fields = ["id", "method", "jsonrpc", "params"]
    auto_increment_id = 0
    @staticmethod
    def json_obj_is(json_obj):
        return all([field in json_obj for field in Request.required_fields])
    @staticmethod
    def from_json(json_obj):
        if not Request.json_obj_is(json_obj):
            raise exception.InvalidReqeust("Message is not a request")
        request = Request(json_obj["id"], json_obj["method"], json_obj["params"], json_obj["jsonrpc"])
        return request
    def __init__(self, method, params, jsonrpc = "2.0"):
        id_ = Request.auto_increment_id
        Request.auto_increment_id += 1
        Message.__init__(self, {"jsonrpc": jsonrpc, "id": id_, "method": method})
        self.params = params

class Response(Message):
    required_fields = ["id", "jsonrpc"]
    @staticmethod
    def json_obj_is(json_obj):
        return all([field in json_obj for field in Response.required_fields]) and ("result" in json_obj or "error" in json_obj)
    @staticmethod
    def from_json(json_obj):
        if not Response.json_obj_is(json_obj):
            raise exception.ParseError("Message is not a response")
        response = Response(json_obj["id"], json_obj["jsonrpc"])
        if "error" in json_obj: response.error = json_obj["error"]
        elif "result" in json_obj: response.result = json_obj["result"]
        else: raise exception.ClientError("Reponse object does not contain error or result")
        return response
        
    def __init__(self, id = None, jsonrpc = "2.0"):
        Message.__init__(self, {"jsonrpc": jsonrpc, "id": id})
