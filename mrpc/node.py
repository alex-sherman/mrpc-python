from __future__ import print_function
import uuid
import time
from collections import defaultdict
from message import Message
from mrpc.path import Path
import mrpc.routing
from proxy import RPCResult
import inspect
from exception import NoReturn

class Node(object):
    
    def __init__(self, guid = None):
        self.transports = []
        self.services = {}
        if guid is None:
            guid = uuid.uuid4()
        self.guid = guid
        self._request_id = 0
        self.callbacks = {}
        self.path_prefix = "/"
        self.register_service(mrpc.routing.Routing())

    def run(self):
        try:
            while any([not transport.closing.is_set() for transport in self.transports]):
                time.sleep(0.1)
        finally:
            [transport.close() for transport in self.transports]

    def request_id(self):
        self._request_id += 1
        return self._request_id

    def use_transport(self, transport):
        self.transports.append(transport)
        transport.begin(self)

    def register_service(self, service, path = None):
        if(path == None):
            path = self.path_prefix + str(type(service).__name__)
        self.services[path] = service

    def rpc(self, path, procedure, value = None, transport = None):
        msg = Message(
            id = self.request_id(),
            src = self.guid.hex,
            dst = path,
            procedure = procedure,
            value = value)
        output = RPCResult()
        self.send(msg, success = output.success, transport = transport)
        return output

    def send(self, message, success = None, failure = None, transport = None):
        self.callbacks[message.id] = (success, failure)
        if transport == None:
            for transport in self.transports:
                transport.send(message)
        else:
            transport.send(message)

    def get_services(self, path):
        return [service for service_path, service in self.services.items()
                    if path.is_match(Path(service_path))]

    def on_recv(self, message):
        dst = Path(message.dst)
        if message.is_response:
            if message.id in self.callbacks:
                success, failure = self.callbacks[message.id]
                try:
                    if hasattr(message, "result"):
                        success(message.result)
                    elif hasattr(message, "error"):
                        failure(exception.JRPCError.from_error(response.error))
                except Exception as e:
                    print("Error:", e)
        elif message.is_request:
            for service in self.get_services(dst):
                method = service.get_method(message.procedure)
                if method:
                    response = Message(
                        id = message.id,
                        src = self.guid.hex,
                        dst = message.src)
                    try:
                        response.result = method(message.value)
                    except NoReturn: return
                    except Exception as e:
                        print("Error:", e)
                        response = None

                    if response:
                        for transport in self.transports:
                            transport.send(response)
