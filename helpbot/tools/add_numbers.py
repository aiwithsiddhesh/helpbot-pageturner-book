SCHEMA = {
      "name": "add_numbers",
      "description": "Adds two numbers and returns the sum.",
      "input_schema": {
          "type": "object",
          "properties": {
              "a": {"type": "number", "description": "First number"},
              "b": {"type": "number", "description": "Second number"},
          },
          "required": ["a", "b"],
      },
  }


def add_numbers(a: float, b: float) -> float:
    return a + b
