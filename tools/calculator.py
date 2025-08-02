"""
Calculator tool for mathematical operations
"""
import math
import operator
from typing import Any
from tools.base import BaseTool
from models.schemas import ToolResult, ToolDefinition


class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations"""
    
    def __init__(self):
        super().__init__("calculator", "Perform mathematical calculations")
        
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
            '%': operator.mod,
        }
        
        self.functions = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'exp': math.exp,
            'abs': abs,
            'round': round,
        }
    
    def execute(self, expression: str) -> ToolResult:
        """Execute mathematical calculation"""
        try:
            # Simple expression evaluation
            # Note: In production, use a more secure approach like ast.literal_eval
            # or a proper expression parser
            result = self._safe_eval(expression)
            return self._create_success_result(result)
        except Exception as e:
            return self._create_error_result(f"Calculation error: {str(e)}")
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate mathematical expression"""
        # Replace common mathematical functions
        expression = expression.replace('sqrt', 'math.sqrt')
        expression = expression.replace('sin', 'math.sin')
        expression = expression.replace('cos', 'math.cos')
        expression = expression.replace('tan', 'math.tan')
        expression = expression.replace('log', 'math.log')
        expression = expression.replace('exp', 'math.exp')
        
        # Use eval with restricted globals (be cautious in production)
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith('__')
        }
        allowed_names.update({'__builtins__': {}})
        
        return eval(expression, allowed_names, {})
    
    def get_tool_definition(self) -> ToolDefinition:
        """Get tool definition for OpenAI function calling"""
        return ToolDefinition(
            type="function",
            function={
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4', 'sqrt(16)')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        )