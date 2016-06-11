from __future__ import print_function
from threading import Thread, Event
import socket
import message
import uuid
import struct
from mrpc import Path
from mrpc import LocalNode

class Transport(object):
    def __init__(self):
        self.closing = Event()
        self.thread = None
        self.thread = TransportThread(self.recv, self.on_recv, self.closing, log = print)
        self.thread.start()

    def send(self, destination, message):
        raise NotImplementedError()

    def recv(self):
        raise NotImplementedError()

    def on_recv(self, message):
        response = message.deserialize(self.socket)
        if not type(response) is message.Response:
            raise exception.JRPCError("Received a message of uknown type")
        if response.id != msg.id: raise exception.JRPCError(0, "Got a response for a different request ID")
        if hasattr(response, "result"):
            return response.result
        elif hasattr(response, "error"):
            raise exception.JRPCError.from_error(response.error)
        raise Exception("Deserialization failure!!")

    def close(self):
        self.closing.set()

class TransportThread(Thread):
    def __init__(self, recv, callback, closing, log = None):
        Thread.__init__(self)
        self.daemon = True
        self.recv = recv
        self.callback = callback
        self.closing = closing
        self._log = log if log is not None else lambda msg: None

    def run(self):
        recvd = ""
        while not self.closing.is_set():
            try:
                source, raw_bytes = self.recv()
                msg = message.from_bytes(raw_bytes)
                if not msg is None:
                    LocalNode.on_recv(source, msg)
                else:
                    print("Message failed to parse")
            except socket.timeout:
                continue
            except Exception as e:
                self.close()
                raise

    def close(self):
        if self.closing.is_set(): return
        self.closing.set()

    def __del__(self):
        self.close()
        del self

class SocketTransport(Transport):
    def __init__(self, local_port = 50123, host = '', remote_port = 50123, timeout = 1, reuseaddr = True, broadcast = "255.255.255.255"):
        self.port = local_port
        self.host = host
        self.remote_port = remote_port
        self.reuseaddr = reuseaddr
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if self.reuseaddr:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.port = self.socket.getsockname()[1]
        self.known_guids = {}
        self.broadcast = broadcast
        Transport.__init__(self)
        print("Service listening on port {0}".format(self.port))

    def recv(self):
        while True:
            try:
                msg_bytes, address = self.socket.recvfrom(4096)
                guid = uuid.UUID(bytes = msg_bytes[:16])
                self.known_guids[guid] = address
                return guid, msg_bytes[16:]
            except socket.timeout:
                continue
            except Exception as e:
                print("An error occured: {0}".format(e))

    def send(self, destination, message):
        socket_dst = None
        if destination == Path.BROADCAST:
            socket_dst = (self.broadcast, self.remote_port)
        elif destination.guid and destination.guid in self.known_guids:
            socket_dst = self.known_guids[destination.guid]
        else:
            raise NotImplementedError()

        self.socket.sendto(LocalNode.guid.bytes + message.bytes, socket_dst)

