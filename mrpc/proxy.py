import message
import threading
from mrpc import LocalNode

class CallThrough(object):
    def __init__(self, path, procedure_name, transport):
        self.transport = transport
        self.path = path
        self.procedure_name = procedure_name
    def __getattr__(self, name):
        return CallThrough(self.procedure_name + "." + name, self.path)
    def __call__(self, *args, **kwargs):
        return Proxy._rpc(self.path, self.procedure_name, self.transport, *args, **kwargs)

class RPCResult(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.completed = False
        self.result = None
        self.actions = []

    def success(self, result):
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
        return self

    def wait(self, timeout = 5):
        self.condition.acquire()
        try:
            while not self.completed:
                self.condition.wait(timeout)
                if timeout and not self.completed:
                    raise Exception("Timeout")
        finally:
            self.condition.release()

    def get(self, timeout = 5):
        self.wait(timeout)
        return self.result

class Proxy(object):
    def __init__(self, target_path = None, transport = None):
        self.next_id = 1
        self.path = target_path
        self.transport = None

    @staticmethod
    def rpc(path, remote_procedure, *args, **kwargs):
        return Proxy._rpc(path, remote_procedure, None, *args, **kwargs)

    @staticmethod
    def _rpc(path, remote_procedure, transport, *args, **kwargs):
        msg = message.Request(
            id = LocalNode.request_id(),
            src = LocalNode.guid.hex,
            dst = path,
            procedure = remote_procedure,
            args = args, kwargs = kwargs)
        output = RPCResult()
        LocalNode.send(msg, success = output.success, transport = transport)
        return output
        
    def __getattr__(self, name):
        return CallThrough(self.path, name, self.transport)