# scripts/test_error.py (fixed)
def add_numbers(a, b):
    return a + b


def greet(name):
    print(f"Hello, {name}!")


very_long_variable_name = (
    "This is a super long string that will exceed the 100 character limit "
    "to test flake8 hooks in pre-commit"
)

print(add_numbers(5, 7))
greet("Alice")
