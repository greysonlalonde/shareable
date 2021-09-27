from .producers import SimpleProducer
from .managers_decorators import on_start
import pickle


@on_start
class Shareable:
    def __init__(self, obj=None):
        factory = SimpleProducer()

        if not isinstance(obj, type(None)):
            self.shared_state = factory.shared_state_a(obj)
        elif isinstance(obj, type(None)):
            self.shared_state = factory.shared_state_b(obj)
        else:
            raise Warning

    def run(self):
        self.shared_state.start()
        print("Connection established")

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
            return str(pickle.loads(self.shared_state.shared_obj[-1]))

    def __repr__(self):
        if not self.shared_state.shared_obj:
            return "Shared state does not exist"
        else:
            return str(pickle.loads(self.shared_state.shared_obj[-1]))

    def __enter__(self):
        return self


if __name__ == "__main__":
    Shareable()
