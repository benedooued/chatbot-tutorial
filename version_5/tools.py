import datetime
import os
import glob

async def get_current_time() -> str:
    """Returns current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def read_local_file(file_path: str) -> str:
    """Reads content from a specified text file or document in the workspace."""
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)  # Read up to first 2000 chars
            return f"--- Content of {file_path} ---\n{content}"
    except Exception as e:
        return f"Error reading file: {e}"

AVAILABLE_TOOLS = [get_current_time, read_local_file]
TOOL_MAP = {
    "get_current_time": get_current_time,
    "read_local_file": read_local_file
}