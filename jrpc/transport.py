from __future__ import print_function
from threading import Thread, Event
import socket
import message
from node import MRPCNode
import uuid
import struct

class Transport(object):
    def __init__(self):
        self.node = MRPCNode.get_self_node()
        self.path = None
        self.closing = Event()
        self.thread = None
        self.services = []
        self.thread = TransportThread(self.recv, self._on_recv, self.closing, log = print)
        self.thread.start()

    def add_service(self, service):
        self.services.append(service)

    def send(self, destination, message):
        raise NotImplementedError()

    def recv(self):
        raise NotImplementedError()

    def _on_recv(self, message):
        pass

    def close():
        self.closing.set()

class TransportThread(Thread):
    def __init__(self, recv, callback, closing, log = None):
        Thread.__init__(self)
        self.recv = recv
        self.callback = callback
        self.closing = closing
        self._log = log if log is not None else lambda msg: None

    def run(self):
        recvd = ""
        while not self.closing.is_set():
            try:
                msg = self.recv()
                if type(msg) is message.Request:
                    response = message.Response(msg.id)
                    method_target = self.service_obj.get_method(msg.method.split('.'))
                    if method_target != None:
                        self.service_obj.lock.acquire()
                        try:
                            response.result = method_target(*msg.params[0], **msg.params[1])
                            self._log("{0} called \"{1}\" returning {2}".format(self.addr, msg.method, json.dumps(response.result)))
                        except Exception as e:
                            self._log("An exception occured while calling {0}: {1}".format(msg.method, e))
                            response.error = exception.exception_to_error(e)
                        finally:
                            self.service_obj.lock.release()
                    else:
                        response.error = {"code": -32601, "message": "No such method {0}".format(msg.method)}
                    
                    response.serialize(self.socket)
                else:
                    self._log("Got a message of uknown type")
            except socket.timeout:
                continue
            except Exception as e:
                self._log("Client socket exception: {0}".format(e))
                break
        self.close()

    def close(self):
        if self.closing.is_set(): return
        self.closing.set()

    def __del__(self):
        self.close()
        del self

class TCPAcceptorThread(Thread):
    def __init__(self, transport):
        Thread.__init__(self)
        self.transport = transport

    def run(self):
        while True:
            try:
                socket_, addr = self.transport.socket.accept()
                print("Got connection from {0}".format(addr))
                socket_.send(self.transport.node.guid.bytes)
                client_guid_bytes = socket_.recv(16)
                if len(client_guid_bytes) < 16:
                    socket_.close()
                    continue
                client_guid = uuid.UUID(bytes = client_guid_bytes)
                self.transport.clients[client_guid] = socket_
            except socket.timeout:
                continue
            except Exception as e:
                print("An error occured: {0}".format(e))

class SocketTransport(Transport):
    def __init__(self, port, host = '', timeout = 1, reuseaddr = True):
        self.port = port
        self.host = host
        self.reuseaddr = reuseaddr
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.reuseaddr:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.port = self.socket.getsockname()[1]              
        self.socket.listen(1)
        self.clients = {}
        self.acceptor = TCPAcceptorThread(self)
        self.acceptor.start()
        Transport.__init__(self)
        print("Service listening on port {0}".format(self.port))

    def recv(self):
        while True:
            for guid, socket_ in self.clients.items():
                try:
                    size_bytes = socket_.recv(4)
                    size = struct.unpack("<L", size_bytes)
                    msg_bytes = socket_.recv(size)
                    return msg_bytes
                except socket.timeout:
                    continue
                except Exception as e:
                    socket_.close()
                    del self.clients[guid]
                    print("An error occured: {0}".format(e))
