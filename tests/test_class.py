class Test:
    def __init__(self, name, age, ss):
        self.name = name
        self.age = age
        self.ss = ss

    def get_details(self):
        return self.name, self.age

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)
