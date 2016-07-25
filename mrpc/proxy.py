import message
import threading
import mrpc

class CallThrough(object):
    def __init__(self, path, procedure_name, mrpc, transport):
        self.transport = transport
        self.path = path + "." + procedure_name
        self.mrpc = mrpc
    def __call__(self, *args, **kwargs):
        value = None
        if args and kwargs: raise ValueError("Cannot call with both args and kwargs")
        if kwargs:
            value = kwargs
        elif args:
            value = args
        return self.mrpc.rpc(self.path, value, self.transport)

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
    def __init__(self, target_path, mrpc, transport):
        self.mrpc = mrpc
        self.next_id = 1
        self.path = target_path
        self.transport = None
        
    def __getattr__(self, name):
        return CallThrough(self.path, name, self.mrpc, self.transport)