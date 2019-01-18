from __future__ import print_function
import uuid
import time
from collections import defaultdict
from .message import Message
from .path import Path
from .proxy import RPCRequest, Proxy
import inspect
from .exception import NoReturn, InvalidPath
from .service import Service, create_service_type
from threading import Thread
from .transport import SocketTransport

class PathCacheEntry(object):
    TIMEOUT = 1
    def __init__(self):
        self.entries = defaultdict(lambda: 0)

    def on_send(self):
        send_time = time.time()
        for uuid in self.entries.keys():
            if self.entries[uuid] == 0:
                self.entries[uuid] = time.time()
            elif (send_time - self.entries[uuid]) > PathCacheEntry.TIMEOUT:
                del self.entries[uuid]
        return set(self.entries.keys())

    def on_recv(self, uuid):
        self.entries[uuid] = 0

    def get_uuids(self):
        return set(self.entries.keys())

class MRPC(object):
    def __init__(self, guid = None, **kwargs):
        self.service = Service(self)
        self.services = {}
        self.transport = SocketTransport(self, **kwargs)
        if guid is None:
            guid = uuid.uuid4()
        self.guid = guid
        self.aliases = [guid.hex]
        self.path_cache = defaultdict(PathCacheEntry)
        self._request_id = 0
        self.requests = {}
        self.path_prefix = "/"
        self.events = []
        self.thread = Thread(target = self.run)
        self.thread.daemon = True
        self.thread.start()
        self.ServiceType = create_service_type(self)

    def Proxy(self, path, **kwargs):
        return Proxy(path, self, **kwargs)

    def run(self):
        try:
            while True:
                if self.events and time.time() >= self.events[0][0]:
                    event = self.events.pop()
                    try:
                        event[1]()
                    except Exception as e:
                        print(e)
                for _id, request in list(self.requests.items()):
                    if request.stale:
                        del self.requests[_id]
                    else:
                        request.poll(self.path_cache[request.message.dst].get_uuids())
                time.sleep(0.1)
        finally:
            self.close()

    def request_id(self):
        self._request_id += 1
        return self._request_id

    def event(self, delay, callback):
        self.events.append((time.time() + delay, callback))
        self.events = sorted(self.events)

    def rpc(self, path, value = None, timeout = 3, resend_delay = 0.5):
        msg = Message(
            id = self.request_id(),
            src = self.guid.hex,
            dst = path,
            value = value)
        output = RPCRequest(msg, timeout, resend_delay, self.transport)
        output.send()
        self.path_cache[path].on_send()
        self.requests[msg.id] = output
        return output

    def srpc(self, path, value = None, timeout = 3, resend_delay = 0.5):
        return self.rpc(path, value, timeout, resend_delay).get()

    def close(self):
        self.transport.close()
        for service in self.services.values():
            try:
                service.close()
            except Exception as e:
                print(e)

    def on_recv(self, message):
        try:
            dst = Path(message.dst)
            if message.is_response:
                if message.id in self.requests:
                    request = self.requests[message.id]
                    self.path_cache[request.message.dst].on_recv(message.src)
                    request.responded.add(message.src)
                    try:
                        if hasattr(message, "result"):
                            request.success(message.result)
                        elif hasattr(message, "error"):
                            request.failure(exception.JRPCError.from_error(response.error))
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
                            self.transport.send(response)
        except InvalidPath:
            pass
