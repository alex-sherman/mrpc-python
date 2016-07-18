from __future__ import print_function
import uuid
import time
from collections import defaultdict
from message import Message
from path import Path
from proxy import RPCResult, Proxy
import inspect
from exception import NoReturn, InvalidPath
from service import Service

class MRPC(object):
    
    def __init__(self, guid = None):
        self.service = Service(self)
        self.services = {}
        @self.service
        def who_has(path):
            try:
                path = Path(path)
                if any([path.is_match(service_name, service, self) for service_name, service in self.services.items()]):
                    return self.guid.hex
            except Exception as e:
                print("Lookup error: ", str(e))
            raise NoReturn()
        who_has.respond("Routing")
        self.transports = []
        if guid is None:
            guid = uuid.uuid4()
        self.guid = guid
        self.aliases = [guid.hex]
        self._request_id = 0
        self.callbacks = {}
        self.path_prefix = "/"
        self.events = []

    def Proxy(self, path, transport = None):
        return Proxy(path, self, transport)

    def run(self):
        try:
            while any([not transport.closing.is_set() for transport in self.transports]):
                if self.events and time.time() >= self.events[0][0]:
                    event = self.events.pop()
                    try:
                        event[1]()
                    except Exception as e:
                        print(e)
                time.sleep(0.1)
        finally:
            self.close()

    def request_id(self):
        self._request_id += 1
        return self._request_id

    def use_transport(self, transport):
        self.transports.append(transport)
        transport.begin(self)

    def event(self, delay, callback):
        self.events.append((time.time() + delay, callback))
        self.events = sorted(self.events)

    def rpc(self, path, value = None, transport = None):
        msg = Message(
            id = self.request_id(),
            src = self.guid.hex,
            dst = path,
            value = value)
        output = RPCResult()
        self.callbacks[msg.id] = (output.success, None)
        if transport == None:
            for transport in self.transports:
                transport.send(msg)
        else:
            transport.send(msg)
        return output

    def close(self):
        [transport.close() for transport in self.transports]
        for service in self.services.values():
            try:
                service.close()
            except Exception as e:
                print(e)

    def on_recv(self, message):
        try:
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
                for service_name, service in self.services.items():
                    if dst.is_match(service_name, service, self):
                        response = Message(
                            id = message.id,
                            src = self.guid.hex,
                            dst = message.src)
                        try:
                            response.result = service(message.value)
                        except NoReturn: return
                        except Exception as e:
                            print("Error:", e)
                            response = None

                        if response:
                            for transport in self.transports:
                                transport.send(response)
        except InvalidPath:
            pass
