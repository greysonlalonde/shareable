
def main():
    """
    >>> from tests.test_class import Test
    >>> from shareable.shareable import Shareable
    >>> t = Test("John Smith", 10, 10)
    >>> s = Shareable(s)
    >>> print(s["name"])
    John Smith
    >>> s["name"] = "about to be deleted"
    >>> print(s["name"])
    about to be deleted
    >>>
    Destroyed shared resources
    Killed all child processes
    """


if __name__ == "__main__":
    import doctest

    doctest.testmod()
