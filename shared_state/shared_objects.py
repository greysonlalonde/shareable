from multiprocessing.resource_tracker import ResourceTracker
from multiprocessing.shared_memory import ShareableList
from multiprocessing.connection import Client, Listener
from multiprocessing.managers import SharedMemoryManager
from abc import ABC, abstractmethod
import psutil
import time
import pickle
import os


class Resources:
    def __init__(self, listener):
        self.listener = listener
        self.conn = listener.accept()

    def __enter__(self):
        try:
            return self.conn.recv()
        except Exception as e:
            return e

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.listener.close()
        self.conn.close()


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
    @abstractmethod
    def __init__(self, obj=None):
        pass

    @abstractmethod
    def start(self, obj=None):
        pass

    def listen(self, func=None, args=None):
        listener = Listener(self.addr, authkey=self.secret)
        with Resources(listener) as message:
            x = 0
            while x == 0:
                if func:
                    if args:
                        x = 1
                        result = func(message)
                    else:
                        result = func()

                    print(f"Function: {func}")
                    return result
                else:
                    print(f"Received message: {message}")
                    self.rec_queue.append(message)
                    x = 1

    def send(self, value):
        with Client(self.addr, authkey=self.secret) as conn:
            conn.send(value)
            conn.send("close")
        self.sent_queue.append(value)

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
            return "Shared object does not exit"
        else:
            return str(pickle.loads(self.shared_obj[-1]).__dict__)

    def __repr__(self):
        if not self.shared_obj:
            return "Shared object does not exist"
        else:
            return str(pickle.loads(self.shared_obj[-1]).__dict__)


class SimpleSharedOne(AbstractShared):
    shared_obj = None
    process_ids = None
    resource_tracker = None
    pid = None
    obj = None

    def __init__(self, obj):
        self.obj = obj
        self.addr = ("localhost", 6000)
        self.secret = bytes("secret".encode("utf-8"))
        self.rec_queue = []
        self.sent_queue = []
        self.pid = os.getpid()

    def start(self, obj=None):
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
        self._unpickled = pickle.loads(self.shared_obj[-1])

    @staticmethod
    def clean_up_one():
        """atexit was double registering, need to find a workaround for this"""
        SimpleSharedOne.clean_up()

    @staticmethod
    def clean_up():
        SimpleSharedOne.shared_obj.shm.close()
        SimpleSharedOne.process_ids.shm.close()
        if not isinstance(SimpleSharedOne.obj, type(None)):
            SimpleSharedOne.shared_obj.shm.unlink()
            SimpleSharedOne.process_ids.shm.unlink()
        SimpleSharedOne.resource_tracker.unregister("SharedState", "shared_memory")
        SimpleSharedOne.resource_tracker.unregister("ProcessId", "shared_memory")
        del SimpleSharedOne.shared_obj
        del SimpleSharedOne.process_ids
        print("Destroyed shared resources")

        p = psutil.Process(SimpleSharedOne.pid)
        for i in p.children(recursive=True):
            p_temp = psutil.Process(i.pid)
            p_temp.kill()
        print(f"Killed all child processes")


class SimpleSharedTwo(AbstractShared):
    shared_obj = None
    process_ids = None
    resource_tracker = None
    pid = None
    obj = None

    def __init__(self, obj):
        self.obj = obj
        self.addr = ("localhost", 6000)
        self.secret = bytes("secret".encode("utf-8"))
        self.rec_queue = []
        self.sent_queue = []
        self.pid = os.getpid()

    def start(self, obj=None):
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
        self._unpickled = pickle.loads(self.shared_obj[-1])

    @staticmethod
    def clean_up():
        print("before2:")
        print(SimpleSharedTwo.shared_obj)
        print(SimpleSharedTwo.process_ids)
        SimpleSharedTwo.shared_obj.shm.close()
        SimpleSharedTwo.process_ids.shm.close()
        print("after2:")
        if not isinstance(SimpleSharedTwo.obj, type(None)):
            print("unlinked")
            SimpleSharedTwo.shared_obj.shm.unlink()
            SimpleSharedTwo.process_ids.shm.unlink()
        SimpleSharedTwo.resource_tracker.unregister("SharedState", "shared_memory")
        SimpleSharedTwo.resource_tracker.unregister("ProcessId", "shared_memory")
        del SimpleSharedTwo.shared_obj
        del SimpleSharedTwo.process_ids
        print("Destroyed shared resources")

        p = psutil.Process(SimpleSharedTwo.pid)
        for i in p.children(recursive=True):
            p_temp = psutil.Process(i.pid)
            p_temp.kill()
        print(f"Killed all child processes")


class ComplexSharedOne(AbstractShared):
    def __init__(self, obj):
        super().__init__(obj)

    def start(self, obj=None):
        self.smm = SharedMemoryManager()
        self.smm.start()
        self.process_ids = self.smm.ShareableList([self.pid])
        self.shared_obj = self.smm.ShareableList([self.pickled])
        self.process_ids[0] = self.pid
        self._unpickled = pickle.loads(self.shared_obj[-1])
        x = 0
        while x == 0:
            try:
                self.send(self.shared_obj.shm.name)
                x = 1
            except ConnectionRefusedError:
                print("Shared instance not found\nTrying again in 5 seconds")
                time.sleep(5)


class ComplexSharedTwo(AbstractShared):
    def __init__(self, obj):
        super().__init__(obj)

    def start(self, obj=None):
        self.listen()
        name = self.rec_queue[0]
        self.process_ids = ShareableList([self.pid])
        self.shared_obj = ShareableList(name=name)
        self.process_ids[0] = self.pid
        self._unpickled = pickle.loads(self.shared_obj[-1])


class SharedStateCreator:
    @staticmethod
    def get_factory(comm_state):
        if not comm_state:
            factory = SimpleProducer()
        else:
            factory = ComplexProducer()

        return factory


if __name__ == "__main__":
    pass
