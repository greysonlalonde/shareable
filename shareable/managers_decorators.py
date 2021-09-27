from multiprocessing.connection import Listener
from threading import Thread
from functools import wraps
import atexit


def on_start(cls):
    @wraps(cls)
    def inner(self=None, *args, **kwargs):
        method = None
        for k, v in cls.__dict__.items():
            if k == "run":
                try:
                    method = cls(self, *args, **kwargs)
                    t = Thread(target=method.run)
                    t.daemon = True
                    t.start()
                    atexit.register(method.shared_state.clean_up)
                except FileNotFoundError:
                    print("Shared object space has not been allocated")
                    break
            if k == "listen":
                try:
                    method = cls(self, *args, **kwargs)
                    t = Thread(target=method.listen)
                    t.daemon = True
                    t.start()
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
        try:
            return self.conn.recv()
        except Exception as e:
            return e

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.close()
        self.close()


if __name__ == "__main__":
    ...
