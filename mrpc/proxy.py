import message
import threading
import mrpc
import time

class Proxy(object):
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
            value = args
        return self.mrpc.rpc(self.path, value, **self.kwargs)

class RPCRequest(object):
    def __init__(self, message, timeout, resend_delay, transports):
        self.transports = transports
        self.creation = time.time()
        self.timeout = timeout
        self.resend_delay = resend_delay
        self.message = message
        self.last_resent = self.creation
        self.responded = set()
        self.condition = threading.Condition()
        self.completed = False
        self.result = None
        self.actions = []

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
        for tranport in self.transports:
            tranport.send(self.message)

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

    def wait(self):
        self.condition.acquire()
        try:
            while not self.completed:
                t = time.time()
                if t >= self.deadline:
                    raise Exception("Timeout")
                self.condition.wait(self.deadline - t)
        finally:
            self.condition.release()

    def get(self, throw = True):
        try:
            self.wait()
            return self.result
        except Exception as e:
            if throw:
                raise
            else:
                return e

    @property
    def stale(self):
        return time.time() >= self.deadline
    
