import datetime
import asyncio

async def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def calculate_expression(expression: str) -> str:
    """Evaluates a basic mathematical expression safely."""
    try:
        # Simple restricted eval for demo purposes
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression."
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Calculation Error: {str(e)}"

AVAILABLE_TOOLS = [get_current_time, calculate_expression]
TOOL_MAP = {
    "get_current_time": get_current_time,
    "calculate_expression": calculate_expression
}