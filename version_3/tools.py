import datetime

def get_current_time() -> str:
    """
    Returns the current date and time in string format.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# List of functions available to the model
AVAILABLE_TOOLS = [get_current_time]
TOOL_MAP = {"get_current_time": get_current_time}