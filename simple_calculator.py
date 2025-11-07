"""Simple command-line calculator."""

def add(a: float, b: float) -> float:
    """Return the sum of ``a`` and ``b``."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of ``a`` and ``b``."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of ``a`` and ``b``."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient of ``a`` and ``b``.

    Raises
    ------
    ZeroDivisionError
        If ``b`` is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def get_number(prompt: str) -> float:
    """Prompt the user for a number until a valid value is provided."""
    while True:
        raw_value = input(prompt)
        try:
            return float(raw_value)
        except ValueError:
            print(f"Invalid number: '{raw_value}'. Please try again.")


def get_operation() -> str:
    """Prompt the user to choose a valid arithmetic operation."""
    operations = {"+": add, "-": subtract, "*": multiply, "/": divide}
    prompt = "Choose an operation (+, -, *, /): "
    while True:
        choice = input(prompt).strip()
        if choice in operations:
            return choice
        print(f"Invalid operation: '{choice}'. Please select one of {', '.join(operations.keys())}.")


def calculate() -> None:
    """Run the calculator workflow."""
    print("Simple Calculator")
    number1 = get_number("Enter the first number: ")
    number2 = get_number("Enter the second number: ")
    operation = get_operation()

    operations = {"+": add, "-": subtract, "*": multiply, "/": divide}
    operation_func = operations[operation]

    try:
        result = operation_func(number1, number2)
    except ZeroDivisionError as error:
        print(error)
        return

    print(f"Result: {result}")


if __name__ == "__main__":
    calculate()
