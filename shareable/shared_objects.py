"""
SharedOne
---------

SharedTwo
---------
"""
from multiprocessing.shared_memory import ShareableList
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.connection import Client
from abc import ABC, abstractmethod
from pickletools import optimize
import pickle
import time
import os
import psutil
from pandas.core.frame import DataFrame
from .managers_decorators import Resources


class AbstractShared(ABC):
    """abstraction of shared objects"""

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
        """
        Starts a shared memory instance
        :return:
            self
        """
        raise NotImplementedError

    @abstractmethod
    def listen(self):
        """
        Starts a listener for a second shared memory instance
        :return:
            self
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, value):
        """
        Sends a message holding the shared memory process name
        :param value:
            shared_memory name
        :return:
            self
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def clean_up(cls):
        """
        Cleans up threads and shared memory process on exit
        :return:
            None
        """
        raise NotImplementedError


class Shared(AbstractShared):
    """parent shared object"""

    shared_obj = None
    obj = None
    shm = SharedMemoryManager()
    pid = os.getpid()
    sent_queue = []
    rec_queue = []
    ADDR = ("localhost", 6000)
    SECRET = bytes("secret".encode("utf-8"))

    def start(self):
        """
        Starts a shared memory instance
        :return:
            self
        """
        ...

    def listen(self):
        """
        Starts a listener for a second shared memory instance
        :return:
            self
        """
        with Resources(self.ADDR, authkey=self.SECRET) as message:
            counter = 0
            while counter == 0:
                self.rec_queue.append(message)
                counter = 1

    def send(self, value):
        """
        Sends a message holding the shared memory process name
        :param value:
            shared_memory name
        :return:
            self
        """
        with Client(self.ADDR, authkey=self.SECRET) as conn:
            conn.send(value)
        self.sent_queue.append(value)

    @classmethod
    def clean_up(cls):
        """
        Cleans up threads and shared memory process on exit
        :return:
            None
        """
        cls.shm.shutdown()
        print("Destroyed shared resources")
        process = psutil.Process(cls.pid)
        for i in process.children(recursive=True):
            p_temp = psutil.Process(i.pid)
            p_temp.kill()
        print("Killed all child processes")


class SharedOne(Shared):
    """shared object child, starts shared mem process"""

    def __init__(self, obj):
        self.obj = obj
        self.shareable = self.pickled()
        SharedOne.obj = self.obj
        self.shm = SharedOne.shm

    def start(self):
        """
        Starts a shared memory instance
        :return:
            self
        """
        self.shm.start()
        self.shared_obj = self.shm.ShareableList([self.pickled()])
        if not isinstance(self.obj, DataFrame):
            self.pop("temp_space")
        SharedOne.shared_obj = self.shared_obj
        iteration = 0
        while iteration == 0:
            try:
                self.send(self.shared_obj.shm.name)
                iteration = 1
            except ConnectionRefusedError:
                time.sleep(5)

        self.pid = os.getpid()
        SharedOne.pid = self.pid
        SharedOne.obj = self.obj

    def pop(self, key):
        """custom method to set shared memory obj attrs"""
        temp = pickle.loads(self.shared_obj[-1])
        temp.__delattr__(key)
        self.shared_obj[-1] = optimize(pickle.dumps(temp))

    def pickled(self):
        """manually allocate memory, I haven't looked into
        whether there is support for 'size=num' for shared_memory
        """
        temp_space = os.urandom(1000)
        self.obj.temp_space = temp_space
        return optimize(pickle.dumps(self.obj))


class SharedTwo(Shared):
    """shared object child, listens for shared mem process"""

    def __init__(self):
        self.shm = SharedTwo.shm

    def start(self):
        """
        Starts a shared memory instance
        :return:
            self
        """
        self.shm.start()
        self.listen()
        name = self.rec_queue[0]
        self.shared_obj = ShareableList(name=name)
        SharedTwo.shared_obj = self.shared_obj


if __name__ == "__main__":
    ...
