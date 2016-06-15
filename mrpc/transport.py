from __future__ import print_function
from threading import Thread, Event
import socket
from message import Message
import uuid
import struct
import mrpc

class Transport(object):
    def __init__(self):
        self.closing = Event()
        self.thread = None
        self.thread = TransportThread(self.recv, self.closing, log = print)
        self.thread.start()
        self.routing = mrpc.Proxy("*/Routing", transport = self)

    def send(self, message):
        raise NotImplementedError()

    def recv(self):
        raise NotImplementedError()

    def close(self):
        self.closing.set()

class TransportThread(Thread):
    def __init__(self, recv, closing, log = None):
        Thread.__init__(self)
        self.daemon = True
        self.recv = recv
        self.closing = closing
        self._log = log if log is not None else lambda msg: None

    def run(self):
        recvd = ""
        while not self.closing.is_set():
            try:
                msg = self.recv()
                if not msg is None:
                    mrpc.LocalNode.on_recv(msg)
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
                msg = Message.from_bytes(msg_bytes)
                if msg != None and msg.is_valid:
                    guid = uuid.UUID(msg.src)
                    self.known_guids[guid] = address
                return msg
            except socket.timeout:
                continue
            except Exception as e:
                print("An error occured: {0}".format(e))

    def send(self, message, guid_dest = None):
        destination = message.dst
        if guid_dest:
            destination = uuid.UUID(guid_dest)
        socket_dst = None
        destination = mrpc.Path(destination)
        if destination.is_broadcast:
            socket_dst = (self.broadcast, self.remote_port)
        elif destination.guid and destination.guid in self.known_guids:
            socket_dst = self.known_guids[destination.guid]

        if socket_dst:
            self.socket.sendto(message.bytes, socket_dst)
        else:
            self.routing.who_has(destination.service).when(lambda guid: self.send(message, guid))


