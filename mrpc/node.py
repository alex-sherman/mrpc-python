import uuid
import time
from collections import defaultdict
from message import Response, Request
from mrpc.path import Path
import mrpc.routing

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

    def register_service(self, service, path = None):
        if(path == None):
            path = str(type(service).__name__)
        self.services[path] = service

    def send(self, message, success = None, failure = None, transport = None):
        self.callbacks[message.id] = (success, failure)
        if transport == None:
            for transport in self.transports:
                transport.send(message)
        else:
            transport.send(message)

    def get_services(self, path):
        return [service for service_path, service in self.services.items()
                    if path.is_match(Path(self.path_prefix + service_path))]

    def on_recv(self, message):
        dst = Path(message.dst)
        if type(message) is Response:
            if message.id in self.callbacks:
                success, failure = self.callbacks[message.id]
                try:
                    if hasattr(message, "result"):
                        success(message.result)
                    elif hasattr(message, "error"):
                        failure(exception.JRPCError.from_error(response.error))
                except Exception as e:
                    print(e)
        elif type(message) is Request:
            for service in self.get_services(dst):
                method = service.get_method(message.procedure.split("."))
                if method:
                    response = Response(
                        id = message.id,
                        src = self.guid.hex,
                        dst = message.src)
                    try:
                        response.result = method(*message.args)
                    except Exception as e:
                        response = None

                    if response:
                        for transport in self.transports:
                            transport.send(response)
