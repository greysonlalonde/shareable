import unittest
from shareable.producers import SimpleProducer
from shareable.shared_objects import Shared, SharedOne, SharedTwo
from tests.test_class import Test

test_class = Test("Nobody", 100, 100)
SHARED_ATTRS = ("ADDR", "SECRET", "shm", "shared_obj", "sent_queue", "rec_queue", "pid")
shared = Shared()


class TestDecorators(unittest.TestCase):
    def test_on_start(self):
        pass


class TestManagers(unittest.TestCase):
    def test_manager(self):
        pass


class TestSharedObjects(unittest.TestCase):
    def test_shared_one(self):
        obj = SharedOne(test_class)
        self.assertIsInstance(obj, SharedOne)

    def test_shared_two(self):
        obj = SharedTwo()
        self.assertIsInstance(obj, SharedTwo)


class TestProducer(unittest.TestCase):
    def test_shared_state_a(self):
        factory = SimpleProducer()
        obj = factory.shared_state_a(test_class)
        self.assertIsInstance(obj, SharedOne)

    def test_shared_state_b(self):
        factory = SimpleProducer()
        obj = factory.shared_state_b()
        self.assertIsInstance(obj, SharedTwo)


class TestShared(unittest.TestCase):
    def test_shared_attrs(self):
        for attr in SHARED_ATTRS:
            self.assertTrue(hasattr(shared, attr), msg=f'obj lacking an attr. obj: {shared}, attr: {attr}')


if __name__ == '__main__':
    unittest.main()
