from . import message
import threading
import time
from .exception import RPCTimeout

class Proxy(object):
    def __init__(self, path, mrpc, **kwargs):
        self.kwargs = kwargs
        self.path = path
        self.mrpc = mrpc
    def __getattr__(self, name):
        return ServiceProxy(self.path + "." + name, self.mrpc, **self.kwargs)

class ServiceProxy(object):
    def __init__(self, path, mrpc, **kwargs):
        self.kwargs = kwargs
        self.path = path
        self.mrpc = mrpc
    def __call__(self, *args, **kwargs):
        value = None
        if args and kwargs: raise ValueError("Cannot call with both args and kwargs")
        if kwargs:
            value = kwargs
        elif args:
            value = args if len(args) > 1 else args[0]
        return self.mrpc.rpc(self.path, value, **self.kwargs)


class RPCRequest(object):
    def __init__(self, message, timeout, resend_delay, transport):
        self.transport = transport
        self.creation = time.time()
        self.timeout = timeout
        self.resend_delay = resend_delay
        self.message = message
        self.last_resent = self.creation
        self.responded = set()
        self.condition = threading.Condition()
        self.completed = False
        self.result = None
        self.error = None
        self.actions = []
        self.error_actions = []

    @property
    def deadline(self):
        return self.creation + self.timeout

    def poll(self, uuids):
        if (uuids and not all([u in self.responded for u in uuids]))\
                and self.resend_delay > 0\
                and time.time() - self.last_resent > self.resend_delay:
            self.send()

    def send(self):
        self.last_resent = time.time()
        self.transport.send(self.message)

    def set_result(self, result):
        self.condition.acquire()
        self.result = result
        self.completed = True
        for action in self.actions:
            action(self.result)
        self.condition.notify()
        self.condition.release()

    def set_error(self, error):
        self.condition.acquire()
        self.error = error
        self.completed = True
        for action in self.error_actions:
            action(self.error)
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

    def wait(self):
        self.condition.acquire()
        try:
            while not self.completed:
                t = time.time()
                if t >= self.deadline:
                    raise RPCTimeout
                self.condition.wait(self.deadline - t)
        finally:
            self.condition.release()

    def get(self, throw = True):
        try:
            self.wait()
            return self.result if not self.error else self.error
        except Exception as e:
            if throw:
                raise
            else:
                return e

    @property
    def stale(self):
        return time.time() >= self.deadline
    
