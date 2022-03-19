"""
SimpleProducer
---------
"""
from abc import ABC, abstractmethod
from shareable.shared_objects import SharedOne, SharedTwo


class AbstractProducer(ABC):
    """
    Abstraction for producer
    """

    @abstractmethod
    def shared_state_a(self):
        """
        Get shared object for shared memory creations.

        :return:
            SharedOne
        """
        raise NotImplementedError

    @abstractmethod
    def shared_state_b(self):
        """
        Get shared object for shared memory connection.

        :return:
            SharedTwo
        """
        raise NotImplementedError


class SimpleProducer(AbstractProducer):
    """
    Implementation of producer.
    """

    def shared_state_a(self, *args):
        """
        Get shared object for shared memory creations.

        :param args:
            object
        :return:
            SharedOne
        """
        return SharedOne(*args)

    def shared_state_b(self):
        """
        Get shared object for shared memory connection.

        :return:
            SharedTwo
        """
        return SharedTwo()
