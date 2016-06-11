import message
import threading
from mrpc import LocalNode

class CallThrough(object):
    def __init__(self, procedure_name, proxy):
        self.proxy = proxy
        self.procedure_name = procedure_name
    def __getattr__(self, name):
        return CallThrough(self.procedure_name + "." + name, self.proxy)
    def __call__(self, *args, **kwargs):
        return self.proxy.rpc(self.procedure_name, args, kwargs)

class RPCResult(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.completed = False
        self.result = None
        self.actions = []

    def complete(self, result):
        self.condition.acquire()
        self.result = result
        self.completed = True
        for action in self.actions:
            action(self.result)
        self.condition.notify()
        self.condition.release()

    def when(self, action):
        self.condition.acquire()
        if not self.completed:
            self.actions.append(action)
        else:
            action(self.result)
        self.condition.release()

    def get(self, timeout = 5):
        self.condition.acquire()
        try:
            while not self.completed:
                self.condition.wait(timeout)
                if timeout and not self.completed:
                    raise Exception("Timeout")
        finally:
            self.condition.release()
        return self.result

class Proxy(object):
    def __init__(self, target_path):
        self.next_id = 1
        self.path = target_path

    def rpc(self, remote_procedure, args, kwargs):
        msg = message.Request(procedure = remote_procedure, args = args, kwargs = kwargs)
        output = RPCResult()
        LocalNode.send(self.path, msg, output.complete)
        return output

    def close(self):
        if "socket" in self.__dict__ and self.socket != None:
            self.socket.close()
        self.socket = None
        
    def __del__(self):
        self.close()
        del self
        
    def __getattr__(self, name):
        return CallThrough(name, self)