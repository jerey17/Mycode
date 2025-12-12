

def kwfunction(x, y, z=1):
    """
    Docstring
    """
    return (x**3 + y) / z


# Define a class with instance variables
class Student:
    """
    Descriptive docstring...
    
    Contains...
    
    """

    # Class attribute
    count = 0

    # Constructor method
    def __init__(self, name='Default', mark=0):
        # Initialise instance attributes
        self.name = name
        self.mark = mark

        # A "private" attribute
        self.__secret = 'HUSH'

        # Access the class attribute
        Student.count += 1
        self.sid = Student.count

        # Initialise empty list
        self.modules = {}

    # Method to print information about class
    def info(self):
        print(f'{self.name}, {self.sid}: {self.mark}')

    # String representation
    def __str__(self):
        return self.name

    # Object representation
    def __repr__(self):
        return f'{type(self).__qualname__}("{self.name}",{self.mark})'

    # An instance method
    def add_submark(self, module, mark):
        if module in self.modules:
            self.modules[module].append(mark)
        else:
            self.modules[module] = [mark]

        self.__update_mark()

    # A private instance method
    def __update_mark(self):
        total = 0
        entries = 0
        for key, value in self.modules.items():
            for v in value:
                total += v
                entries += 1

                self.mark = total / entries
                
    # Polymorphism: operator overloading
    def __add__(self, other):
        return f'{self.name} and {other.name}'
    
    # Polymorphism: allow subclasses to define behaviour
    def classification(self):
        raise NotImplementedError("Subclass must implement abstract method.")
        

# When running as a script:
if __name__ == "__main__":
    print(f'This file is being run as a script and is called: {__name__}.')
else:
    print(f'This file is being imported and is called: {__name__}.')
