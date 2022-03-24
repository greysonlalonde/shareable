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
import logging
from pickletools import optimize
import pickle
import time
import os
import psutil
from pandas.core.frame import DataFrame
from shareable.managers_decorators import Resources

logging.basicConfig(format='%(message)s', level=logging.INFO)


class AbstractShared(ABC):
    """Abstraction of shared objects."""

    @classmethod
    def __init_subclass__(cls):
        required_class_attrs = [
            "shm",
            "shared_obj",
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
            None
        """
        raise NotImplementedError

    @abstractmethod
    def listen(self):
        """
        Starts a listener for a second shared memory instance
        :return:
            None
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, value):
        """
        Sends a message holding the shared memory process name
        :param value:
            shared_memory name
        :return:
            None
        """
        raise NotImplementedError

    @abstractmethod
    def clean_up(self):
        """
        Cleans up threads and shared memory process on exit
        :return:
            None
        """
        raise NotImplementedError


class Shared(AbstractShared):
    """parent shared object"""

    ADDR = ("localhost", 6000)
    SECRET = bytes("secret".encode("utf-8"))
    shm = None
    shared_obj = None
    sent_queue = []
    rec_queue = []
    pid = os.getpid()

    def start(self):
        pass

    def listen(self):
        """
        Starts a listener for a second shared memory instance
        :return:
            self
        """
        socket = self.ADDR[1]
        while True:
            try:
                with Resources(self.ADDR, authkey=self.SECRET) as message:
                    counter = 0
                    while counter == 0:
                        self.rec_queue.append(message)
                        counter = 1
                    break
            except OSError:
                socket += 1
                logging.info(f"Socket {(socket - 1)} is in use, trying {socket}")

    def send(self, value):
        """
        Sends a message holding the shared memory process name.

        :param value:
            shared_memory name
        :return:
            self
        """
        with Client(self.ADDR, authkey=self.SECRET) as conn:
            conn.send(value)
        self.sent_queue.append(value)

    def clean_up(self):
        """
        Cleans up threads and shared memory process on exit.

        :return:
            None
        """
        self.shm.shutdown()
        logging.info("Destroyed shared resources")
        process = psutil.Process(self.pid)
        for i in process.children(recursive=True):
            p_temp = psutil.Process(i.pid)
            p_temp.kill()
        logging.info("Killed all child processes")


class SharedOne(Shared):
    """
    Shared object child, starts shared mem process.
    """

    def __init__(self, obj):
        self.obj = obj
        self.shareable = self.pickled()
        self.pid = os.getpid()
        self.shm = SharedMemoryManager()
        self.shm.start()
        self.shared_obj = self.shm.ShareableList([self.pickled()])

    def start(self):
        """
        Starts a shared memory instance.

        :return:
            None
        """
        if not isinstance(self.obj, DataFrame):
            self.pop("temp_space")
        iteration = 0
        while iteration == 0:
            try:
                self.send(self.shared_obj.shm.name)
                iteration = 1
            except ConnectionRefusedError:
                time.sleep(5)

    def pop(self, key):
        """
        Custom pop method to set shared memory obj attrs.

        :param key:
            ...
        :return:
            None
        """
        temp = pickle.loads(self.shared_obj[-1])
        temp.__delattr__(key)
        self.shared_obj[-1] = optimize(pickle.dumps(temp))

    def pickled(self):
        """
        Manually allocate memory, I haven't looked into
        whether there is support for 'size=num' for shared_memory.

        :return:
            object
        """
        temp_space = os.urandom(1000)
        self.obj.temp_space = temp_space
        # if not isinstance(dict, self.obj):
        #     self.obj.temp_space = temp_space
        # else:
        #     self.obj['temp_space'] = temp_space
        return optimize(pickle.dumps(self.obj))


class SharedTwo(Shared):
    """
    shared object child, listens for shared mem process
    """

    def __init__(self):
        self.shared_obj = None
        self.shm = SharedMemoryManager()

    def start(self):
        """
        Starts a shared memory instance.

        :return:
            None
        """
        self.shm.start()
        self.listen()
        name = self.rec_queue[0]
        self.shared_obj = ShareableList(name=name)
