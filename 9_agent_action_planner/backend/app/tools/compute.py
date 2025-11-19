# app/tools/compute.py

from app.tools.base import BaseTool


class ComputeTool(BaseTool):
    """
    Simple computation tool used by the Executor to perform math tasks.
    """

    name: str = "compute"
    description: str = "Performs arithmetic calculations safely."

    async def run(self, expression: str) -> str:
        """
        Safely evaluates a simple math expression (no builtins, no variables).
        Supports +, -, *, /, parentheses.
        """

        allowed_chars = "0123456789+-*/(). "
        if any(ch not in allowed_chars for ch in expression):
            return "Invalid characters in expression."

        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Computation error: {str(e)}"