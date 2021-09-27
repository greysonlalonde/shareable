class Test:
    def __init__(self, name, age, ss):
        self.name = name
        self.age = age
        self.ss = ss

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)
