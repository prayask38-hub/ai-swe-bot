class Greeter:
    def __init__(self, name):
        # Initialize the Greeter class with a name
        self.name = name
    def greet(self):
        # Print a greeting message
        print(f'Hello, {self.name}!')

greeter = Greeter('World')
greeter.greet()