"""
on_start
---------

Resources
---------
"""
from multiprocessing.connection import Listener
from threading import Thread
from functools import wraps
import atexit


def on_start(cls):
    """starts shared_memory multiprocessing instance & run methods"""

    @wraps(cls)
    def inner(*args, **kwargs):
        method = None
        for key in cls.__dict__.keys():
            if key == "run":
                try:
                    method = cls(*args, **kwargs)
                    thread = Thread(target=getattr(method, key))
                    thread.daemon = True
                    thread.start()
                    atexit.register(method.shared_state.clean_up)
                except FileNotFoundError:
                    print("Shared object space has not been allocated")
                    break
        return method

    return inner


class Resources(Listener):
    """
    Resource manager for receiving messages between processes
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = self.accept()

    def __enter__(self):
        return self.conn.recv()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.close()
        self.close()


if __name__ == "__main__":
    ...
