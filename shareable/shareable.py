"""
Shareable
---------
"""
import pickle
import logging
from pickletools import optimize
from shareable.producers import SimpleProducer
from shareable.managers_decorators import on_start


logging.basicConfig(format='%(message)s', level=logging.INFO)


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
        else:
            self.shared_state = factory.shared_state_b()

    def run(self):
        """
        Interface to shared obj start method.

        :return:
            None
        """
        self.shared_state.start()
        logging.info("Connection established")

    def methods(self):
        """
        Get all methods belonging to a shared obj.

        :return:
            list
        """
        method_list = [
            method
            for method in dir(self.shared_elements())
            if method.startswith("__") is False
        ]
        return method_list

    def shared_elements(self):
        """
        Load shared obj from pickle.

        :return:
            shared obj
        """
        return pickle.loads(self.shared_state.shared_obj[-1])

    def __delitem__(self, key):
        """
        del method

        :param key:
            ...
        :return:
            None
        """
        self.__delattr__(key)

    def __getitem__(self, key):
        """
        getter method

        :param key:
            ...
        :return:
            attr
        """
        return getattr(self.shared_elements(), key)

    def __setitem__(self, key, value, inplace=False):
        """
        setter method

        :param key:
            ...
        :param value:
            ...
        :param inplace:
            bool
        :return:
            None
        """
        obj = self.shared_elements()
        obj.__setattr__(key, value)
        self.shared_state.shared_obj[-1] = optimize(pickle.dumps(obj))

    def __str__(self):
        """
        __str__ method

        :return:
            str`
        """
        return (
            "Shared object does not exist"
            if not self.shared_state.shared_obj
            else str(self.shared_elements())
        )

    def __repr__(self):
        """
        repr method

        :return:
            str
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

        :return:
            self
        """
        return self


if __name__ == "__main__":
    Shareable()
