"""
SimpleProducer
---------
"""
from abc import ABC, abstractmethod
from shareable.shared_objects import SharedOne, SharedTwo


class AbstractProducer(ABC):
    """abstraction for producer"""

    @abstractmethod
    def shared_state_a(self):
        """
        get shared object for shared memory creations
        :return:
            SharedOne
        """
        raise NotImplementedError

    @abstractmethod
    def shared_state_b(self):
        """
        get shared object for shared memory connection
        :return:
            SharedTwo
        """
        raise NotImplementedError


class SimpleProducer(AbstractProducer):
    """implementation of producer"""

    def shared_state_a(self, *args):
        """
        get shared object for shared memory creations
        :param args:
            object
        :return:
            SharedOne
        """
        return SharedOne(*args)

    def shared_state_b(self):
        """
        get shared object for shared memory connection
        :return:
            SharedTwo
        """
        return SharedTwo()
