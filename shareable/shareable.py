"""
Shareable
---------
"""
import pickle
from pickletools import optimize
from .producers import SimpleProducer
from .managers_decorators import on_start


@on_start
class Shareable:
    """
    Interface to shared memory objects

    Parameters
    ----------
    obj:
        None or object

    Examples
    ----------
    >>> from shareable import Shareable
    >>> from tests.test_class import Test
    >>> test = Test('DB Cooper', 50, 0)
    >>> s = Shareable(test)
    Shareable(DB Cooper, 50, 0)
    """

    def __init__(self, obj=None):
        factory = SimpleProducer()

        if not isinstance(obj, type(None)):
            self.shared_state = factory.shared_state_a(obj)
        elif isinstance(obj, type(None)):
            self.shared_state = factory.shared_state_b()
        else:
            raise Warning

    def run(self):
        """
        interface to shared obj start method
        """
        self.shared_state.start()
        print("Connection established")

    def methods(self):
        """
        get all methods belonging to a shared obj
        """
        method_list = [
            method
            for method in dir(self.shared_elements())
            if method.startswith("__") is False
        ]
        return method_list

    def shared_elements(self):
        """
        laod shared obj from pickle
        """
        return pickle.loads(self.shared_state.shared_obj[-1])

    def __delitem__(self, key):
        """
        del method
        """
        self.__delattr__(key)

    def __getitem__(self, key):
        """
        getter method
        """
        return getattr(self.shared_elements(), key)

    def __setitem__(self, key, value, inplace=False):
        """
        setter method
        """
        obj = self.shared_elements()
        obj.__setattr__(key, value)
        self.shared_state.shared_obj[-1] = optimize(pickle.dumps(obj))

    def __str__(self):
        """
        __str__ method
        """
        if not self.shared_state.shared_obj:
            string = "Shared object does not exist"
        else:
            string = str(self.shared_elements())
        return string

    def __repr__(self):
        """
        repr method
        """
        if not self.shared_state.shared_obj:
            obj_repr = "Shared state does not exist"
        else:
            obj = self.shared_elements()
            obj_repr = (
                f"Shareable({', '.join([str(v) for v in obj.__dict__.values()])})"
            )
        return obj_repr

    def __enter__(self):
        """
        enter method
        """
        return self


if __name__ == "__main__":
    Shareable()
