import unittest
from shareable.producers import SimpleProducer
from shareable.shared_objects import SharedOne, SharedTwo
from tests.test_class import Test

test_class = Test("Nobody", 100, 100)


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


if __name__ == '__main__':
    unittest.main()
