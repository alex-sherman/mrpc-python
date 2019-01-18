from __future__ import print_function
from threading import Thread, Event
import socket
from .message import Message
import uuid
import struct
from .proxy import Proxy
from .path import Path

class TransportThread(Thread):
    def __init__(self, recv, closing, node):
        Thread.__init__(self)
        self.daemon = True
        self.recv = recv
        self.closing = closing
        self.node = node

    def run(self):
        recvd = ""
        while not self.closing.is_set():
            try:
                msg = self.recv()
                if not msg is None:
                    self.node.on_recv(msg)
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

class SocketTransport(object):
    def __init__(self, node, local_port = 50123, host = '0.0.0.0', remote_port = 50123,
                    timeout = 1, reuseaddr = True, broadcast = "255.255.255.255"):
        self.closing = Event()
        socket.setdefaulttimeout(timeout)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if reuseaddr:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, local_port)) 
        self.thread = TransportThread(self.recv, self.closing, node)
        self.thread.start()
        self.remote_port = remote_port
        self.known_guids = {}
        self.broadcast = broadcast

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

    def send(self, message):
        socket_dst = (self.broadcast, self.remote_port)
        dst = Path(message.dst)
        if dst.guid and dst.guid in self.known_guids:
            socket_dst = self.known_guids[dst.guid]
        self.socket.sendto(message.bytes, socket_dst)

    def close(self):
        self.closing.set()
