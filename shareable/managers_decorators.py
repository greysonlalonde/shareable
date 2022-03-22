"""
on_start
---------

Resources
---------
"""
from multiprocessing.connection import Listener
from threading import Thread
from functools import wraps
import logging
import atexit

logging.basicConfig(format='%(message)s', level=logging.INFO)


def on_start(cls):
    """
    Starts shared_memory multiprocessing instance,
    run methods and registers instance for cleanup.

    :return:
        ...
    """

    @wraps(cls)
    def inner(*args, **kwargs):
        method = None
        for key in cls.__dict__.keys():
            if key == "run":
                # starts and registers thread for cleanup
                try:
                    method = cls(*args, **kwargs)
                    thread = Thread(target=getattr(method, key))
                    thread.daemon = True
                    thread.start()
                    atexit.register(method.shared_state.clean_up)
                except FileNotFoundError:
                    logging.info("Shared object space has not been allocated")
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
        """
        __enter__ method

        :return:
            bool
        """
        return self.conn.recv()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        __exit__ method

        :param exc_type:
            str
        :param exc_value:
            str
        :param exc_traceback:
            str
        :return:
            None
        """
        self.conn.close()
        self.close()
