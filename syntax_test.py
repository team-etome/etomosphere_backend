# This is a comment
def hello_world():
    """This is a docstring"""
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    hello_world()
    test = TestClass("Etomosphere")
    print(test.greet())






