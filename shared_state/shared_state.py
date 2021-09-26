from .shared_objects import SharedStateCreator
from functools import wraps
import pickle
import atexit
import psutil


def on_start(cls):
    @wraps(cls)
    def inner(self=None, *method_args, **method_kwargs):
        method = None
        for k, v in cls.__dict__.items():
            if k == "run":
                try:
                    method = cls(self, *method_args, **method_kwargs)
                    method.run()
                    atexit.register(method.shared_state.clean_up)
                except FileNotFoundError:
                    print("Shared object space has not been allocated")
                    break
        return method

    return inner


@on_start
class SharedState:
    def __init__(self, obj=None, comm_state=None):
        self.obj = obj
        factory = SharedStateCreator.get_factory(comm_state)
        if not isinstance(obj, type(None)) and not comm_state:
            self.shared_state = factory.shared_state_a(obj)
        elif isinstance(obj, type(None)) and not comm_state:
            self.shared_state = factory.shared_state_b(obj)

        elif not isinstance(obj, type(None)) and comm_state:
            self.shared_state = factory.shared_state_a(obj)
        else:
            self.shared_state = factory.shared_state_b(obj)

    def run(self):
        self.shared_state.start()
        if not isinstance(self.obj, type(None)):
            try:
                self.pop("b")
            # for pandas objects
            except ValueError:
                print("Not a pandas object")

    def methods(self):
        method_list = [
            method
            for method in dir(self.shared_elements)
            if method.startswith("__") is False
        ]
        return method_list

    @property
    def shared_elements(self):
        return pickle.loads(self.shared_state.shared_obj[-1])

    def get_processes(self):
        li = []
        p = psutil.Process(self.shared_state.pid)
        for i in p.children(recursive=True):
            p_temp = psutil.Process(i.pid)
            li.append(p_temp)
        return li

    def pop(self, key):
        temp = pickle.loads(self.shared_state.shared_obj[-1])
        temp.__delattr__(key)
        self.shared_state.shared_obj[-1] = pickle.dumps(temp)

    def __delitem__(self, key):
        self.__delattr__(key)

    def __getitem__(self, key):
        temp = pickle.loads(self.shared_state.shared_obj[-1])
        return temp.__getattribute__(key)

    def __setitem__(self, key, value):
        temp = pickle.loads(self.shared_state.shared_obj[-1])
        temp.__setattr__(key, value)
        self.shared_state.shared_obj[-1] = pickle.dumps(temp)

    def __str__(self):
        if not self.shared_state.shared_obj:
            return "Shared object does not exist"
        else:
            return str(pickle.loads(self.shared_state.shared_obj[-1]).__dict__)

    def __repr__(self):
        if not self.shared_state.shared_obj:
            return "Shared state does not exist"
        else:
            return str(pickle.loads(self.shared_state.shared_obj[-1]).__dict__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shared_state.clean_up()


if __name__ == "__main__":
    SharedState()
