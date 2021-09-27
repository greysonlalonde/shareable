from abc import ABC, abstractmethod
from .shared_objects import SharedOne, SharedTwo


class AbstractProducer(ABC):
    @abstractmethod
    def shared_state_a(self):
        pass

    @abstractmethod
    def shared_state_b(self):
        pass


class SimpleProducer(AbstractProducer):
    def shared_state_a(self, *args):
        return SharedOne(*args)

    def shared_state_b(self, *args):
        return SharedTwo()
