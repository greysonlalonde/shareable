from multiprocessing.resource_tracker import ResourceTracker
from multiprocessing.shared_memory import ShareableList
from multiprocessing.managers import SharedMemoryManager
from shared_state.managers_decorators import Resources
from multiprocessing.connection import Client
from abc import ABC, abstractmethod
import psutil
import pickle
import time
import os


class AbstractProducer(ABC):
    @abstractmethod
    def shared_state_a(self):
        pass

    @abstractmethod
    def shared_state_b(self):
        pass


class SimpleProducer(AbstractProducer):
    def shared_state_a(self, *args):
        return SimpleSharedOne(*args)

    def shared_state_b(self, *args):
        return SimpleSharedTwo(*args)


class ComplexProducer(AbstractProducer):
    def shared_state_a(self, *args):
        return ComplexSharedOne(*args)

    def shared_state_b(self, *args):
        return ComplexSharedTwo(*args)


class AbstractShared(ABC):
    resource_tracker = None
    process_ids = None
    shared_obj = None
    obj = None
    pid = os.getpid()
    sent_queue = []
    rec_queue = []
    addr = ("localhost", 6000)
    secret = bytes("secret".encode("utf-8"))

    def listen(self, func=None, args=None):
        with Resources(self.addr, authkey=self.secret) as message:
            x = 0
            while x == 0:
                if func or args:
                    result = func(message)
                    print(f"Function: {func}")
                    return result
                else:
                    print(f"Received message: {message}")
                    self.rec_queue.append(message)
                    x = 1

    def send(self, value):
        with Client(self.addr, authkey=self.secret) as conn:
            conn.send(value)
        self.sent_queue.append(value)

    @classmethod
    def clean_up(cls):
        cls.shared_obj.shm.close()
        cls.process_ids.shm.close()
        if not isinstance(cls.obj, type(None)):
            cls.shared_obj.shm.unlink()
            cls.process_ids.shm.unlink()
        cls.resource_tracker.unregister("SharedState", "shared_memory")
        cls.resource_tracker.unregister("ProcessId", "shared_memory")
        del cls.shared_obj
        del cls.process_ids
        print("Destroyed shared resources")

        p = psutil.Process(cls.pid)
        for i in p.children(recursive=True):
            p_temp = psutil.Process(i.pid)
            p_temp.kill()
        print(f"Killed all child processes")

    @property
    def pickled(self):
        """manually allocate memory, I haven't looked into
        whether there is support for 'size=num' for shared_memory
        """
        b = os.urandom(1000)
        self.obj.b = b
        return pickle.dumps(self.obj)

    def __delitem__(self, key):
        self.__delattr__(key)

    def __getitem__(self, key):
        temp = pickle.loads(self.shared_obj[-1])
        return temp.__getattribute__(key)

    def __setitem__(self, key, value):
        temp = pickle.loads(self.shared_obj[-1])
        temp.__setattr__(key, value)
        self.shared_obj[-1] = pickle.dumps(temp)

    def __str__(self):
        if not self.shared_obj:
            return "Shared object does not exist"
        else:
            return str(pickle.loads(self.shared_obj[-1]).__dict__)

    def __repr__(self):
        if not self.shared_obj:
            return "Shared object does not exist"
        else:
            return str(pickle.loads(self.shared_obj[-1]).__dict__)


class SimpleSharedOne(AbstractShared):
    def __init__(self, obj):
        self.obj = obj

    def start(self):
        self.shared_obj = ShareableList([self.pickled], name="SharedState")
        self.process_ids = ShareableList(["" for i in range(10)], name="ProcessId")
        self.resource_tracker = ResourceTracker()
        self.resource_tracker.register(self.shared_obj.shm.name, "shared_memory")
        self.resource_tracker.register(self.process_ids.shm.name, "shared_memory")
        SimpleSharedOne.shared_obj = self.shared_obj
        SimpleSharedOne.process_ids = self.process_ids
        SimpleSharedOne.resource_tracker = self.resource_tracker
        self.pid = os.getpid()
        self.process_ids[0] = self.pid
        SimpleSharedOne.pid = self.pid
        SimpleSharedOne.obj = self.obj


class SimpleSharedTwo(AbstractShared):
    def __init__(self, obj=None):
        self.obj = obj

    def start(self):
        self.shared_obj = ShareableList(name="SharedState")
        self.process_ids = ShareableList(name="ProcessId")
        self.resource_tracker = ResourceTracker()
        self.resource_tracker.register(self.shared_obj.shm.name, "shared_memory")
        self.resource_tracker.register(self.process_ids.shm.name, "shared_memory")
        SimpleSharedTwo.shared_obj = self.shared_obj
        SimpleSharedTwo.shared_obj = self.shared_obj
        SimpleSharedTwo.process_ids = self.process_ids
        SimpleSharedTwo.resource_tracker = self.resource_tracker
        SimpleSharedTwo.pid = self.pid
        SimpleSharedTwo.obj = self.obj
        self.process_ids[0] = self.pid


class ComplexSharedOne(AbstractShared):
    smm = SharedMemoryManager()

    def __init__(self, obj, settings=True):
        self.settings = settings
        self.obj = obj
        self.smm = ComplexSharedOne.smm

    def start(self):
        self.smm.start()
        self.process_ids = self.smm.ShareableList([self.pid])
        self.shared_obj = self.smm.ShareableList([self.pickled])
        self.process_ids[0] = self.pid
        x = 0
        while x == 0:
            try:
                self.send(self.shared_obj.shm.name)
                x = 1
            except ConnectionRefusedError:
                print("Shared instance not found\nTrying again in 5 seconds")
                time.sleep(5)


class ComplexSharedTwo(AbstractShared):
    smm = SharedMemoryManager()

    def __init__(self, obj=None, settings=True):
        self.settings = settings
        self.obj = obj
        self.smm = ComplexSharedTwo.smm

    def start(self):
        self.listen()
        name = self.rec_queue[0]
        self.process_ids = ShareableList([self.pid])
        self.shared_obj = ShareableList(name=name)
        self.process_ids[0] = self.pid


class SharedStateCreator:
    @staticmethod
    def get_factory(comm_state):
        if not comm_state:
            factory = SimpleProducer()
        else:
            factory = ComplexProducer()

        return factory


if __name__ == "__main__":
    ...
