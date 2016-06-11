import uuid
import time
from collections import defaultdict
from message import Response, Request
from mrpc.path import Path

class Node(object):
    
    def __init__(self, guid = None):
        self.transports = []
        self.service = None
        if guid is None:
            guid = uuid.uuid4()
        self.guid = guid
        self.id_ = 0
        self.callbacks = {}

    def run(self):
        try:
            while any([not transport.closing.is_set() for transport in self.transports]):
                time.sleep(0.1)
        finally:
            [transport.close() for transport in self.transports]

    def use_transport(self, transport):
        self.transports.append(transport)

    def set_service(self, service):
        self.service = service

    def send(self, destination, message, callback = None):
        message.id = self.id_
        self.id_ += 1
        if callback:
            self.callbacks[message.id] = callback
        for transport in self.transports:
            transport.send(destination, message)

    def on_recv(self, source, message):
        if type(message) is Response:
            if message.id in self.callbacks:
                self.callbacks[message.id](message.result)
        elif type(message) is Request and self.service != None:
            method = self.service.get_method(message.procedure.split("."))
            if method:
                result = method(*message.args)
                response = Response(id = message.id, result = result)
                for transport in self.transports:
                    transport.send(Path.parse(source), response)
