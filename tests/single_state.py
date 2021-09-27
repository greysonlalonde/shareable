from shareable.shareable import SharedState
from test_class import Shareable


def main():
    """
    >>> s = Shareable("John Smith", 10, 10)
    >>> ss = SharedState(s)
    >>> print(ss["name"])
    John Smith
    >>> ss["name"] = "about to be deleted"
    >>> print(ss["name"])
    about to be deleted
    >>>
    Destroyed shared resources
    Killed all child processes
    """


if __name__ == "__main__":
    import doctest

    doctest.testmod()
