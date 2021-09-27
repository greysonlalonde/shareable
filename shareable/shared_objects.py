from multiprocessing.shared_memory import ShareableList
from multiprocessing.managers import SharedMemoryManager
from .managers_decorators import Resources
from multiprocessing.connection import Client
from pandas.core.frame import DataFrame
from abc import ABC, abstractmethod
import psutil
import pickle
import time
import os


class AbstractShared(ABC):
    shm = SharedMemoryManager()
    resource_tracker = None
    process_ids = None
    shared_obj = None
    obj = None
    pid = os.getpid()
    sent_queue = []
    rec_queue = []
    ADDR = ("localhost", 6000)
    SECRET = bytes("secret".encode("utf-8"))

    @abstractmethod
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


class SharedOne(AbstractShared):
    def __init__(self, obj):
        self.obj = obj
        self.shareable = self.pickled()
        SharedOne.obj = self.obj
        self.shm = SharedOne.shm

    def start(self):
        self.shm.start()
        self.process_ids = self.shm.ShareableList([self.pid])
        self.shared_obj = self.shm.ShareableList([self.pickled()])
        if not isinstance(self.obj, DataFrame):
            self.pop("b")
        SharedOne.process_ids = self.process_ids
        SharedOne.shared_obj = self.shared_obj
        self.process_ids[0] = self.pid
        x = 0
        while x == 0:
            try:
                self.send(self.shared_obj.shm.name)
                x = 1
            except ConnectionRefusedError:
                time.sleep(5)

        self.pid = os.getpid()
        self.process_ids[0] = self.pid
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
        b = os.urandom(1000)
        self.obj.b = b
        return pickle.dumps(self.obj)


class SharedTwo(AbstractShared):
    def __init__(self):
        self.shm = SharedTwo.shm

    def start(self):
        self.shm.start()
        self.listen()
        name = self.rec_queue[0]
        self.process_ids = ShareableList([self.pid])
        self.shared_obj = ShareableList(name=name)
        SharedTwo.process_ids = self.process_ids
        SharedTwo.shared_obj = self.shared_obj
        self.process_ids[0] = self.pid


if __name__ == "__main__":
    ...
