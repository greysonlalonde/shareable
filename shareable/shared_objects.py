from multiprocessing.shared_memory import ShareableList
from multiprocessing.managers import SharedMemoryManager
from .managers_decorators import Resources
from multiprocessing.connection import Client
from pandas.core.frame import DataFrame
from abc import ABC, abstractmethod
from pickletools import optimize
import psutil
import pickle
import time
import os


class AbstractShared(ABC):

    @classmethod
    def __init_subclass__(cls):
        required_class_attrs = [
            "shm",
            "shared_obj",
            "obj",
            "pid",
            "sent_queue",
            "rec_queue",
            "ADDR",
            "SECRET",
        ]
        for attr in required_class_attrs:
            if not hasattr(cls, attr):
                raise NotImplementedError(f"{cls} missing required {attr} attr")

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def listen(self):
        pass

    @abstractmethod
    def send(self, value):
        pass

    @classmethod
    @abstractmethod
    def clean_up(cls):
        pass


class Shared(AbstractShared):
    shared_obj = None
    obj = None
    shm = SharedMemoryManager()
    pid = os.getpid()
    sent_queue = []
    rec_queue = []
    ADDR = ("localhost", 6000)
    SECRET = bytes("secret".encode("utf-8"))

    def start(self):
        pass

    def listen(self, func=None, args=None):
        with Resources(self.ADDR, authkey=self.SECRET) as message:
            x = 0
            while x == 0:
                if func or args:
                    result = func(message)
                    print(f"Function: {func}")
                    return result
                else:
                    self.rec_queue.append(message)
                    x = 1

    def send(self, value):
        with Client(self.ADDR, authkey=self.SECRET) as conn:
            conn.send(value)
        self.sent_queue.append(value)

    @classmethod
    def clean_up(cls):
        cls.shm.shutdown()
        print("Destroyed shared resources")
        p = psutil.Process(cls.pid)
        for i in p.children(recursive=True):
            p_temp = psutil.Process(i.pid)
            p_temp.kill()
        print("Killed all child processes")


class SharedOne(Shared):
    def __init__(self, obj):
        self.obj = obj
        self.shareable = self.pickled()
        SharedOne.obj = self.obj
        self.shm = SharedOne.shm

    def start(self):
        self.shm.start()
        self.shared_obj = self.shm.ShareableList([self.pickled()])
        if not isinstance(self.obj, DataFrame):
            self.pop("temp_space")
        SharedOne.shared_obj = self.shared_obj
        x = 0
        while x == 0:
            try:
                self.send(self.shared_obj.shm.name)
                x = 1
            except ConnectionRefusedError:
                time.sleep(5)

        self.pid = os.getpid()
        SharedOne.pid = self.pid
        SharedOne.obj = self.obj

    def pop(self, key):
        temp = pickle.loads(self.shared_obj[-1])
        temp.__delattr__(key)
        self.shared_obj[-1] = pickle.dumps(temp)

    def pickled(self):
        """manually allocate memory, I haven't looked into
        whether there is support for 'size=num' for shared_memory
        """
        temp_space = os.urandom(1000)
        self.obj.temp_space = temp_space
        return optimize(pickle.dumps(self.obj))


class SharedTwo(Shared):
    def __init__(self):
        self.shm = SharedTwo.shm

    def start(self):
        self.shm.start()
        self.listen()
        name = self.rec_queue[0]
        self.shared_obj = ShareableList(name=name)
        SharedTwo.shared_obj = self.shared_obj


if __name__ == "__main__":
    ...
