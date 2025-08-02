"""
Tests for Calculator tool
"""
import pytest
import math

from tools.calculator import CalculatorTool
from models.schemas import ToolDefinition


class TestCalculatorTool:
    """Test Calculator tool functionality"""
    
    @pytest.fixture
    def calculator(self):
        """Calculator tool fixture"""
        return CalculatorTool()
    
    def test_initialization(self, calculator):
        """Test calculator initialization"""
        assert calculator.name == "calculator"
        assert calculator.description == "Perform mathematical calculations"
    
    def test_basic_arithmetic(self, calculator):
        """Test basic arithmetic operations"""
        # Addition
        result = calculator.execute(expression="2 + 3")
        assert result.success is True
        assert result.result == 5
        
        # Subtraction
        result = calculator.execute(expression="10 - 4")
        assert result.success is True
        assert result.result == 6
        
        # Multiplication
        result = calculator.execute(expression="6 * 7")
        assert result.success is True
        assert result.result == 42
        
        # Division
        result = calculator.execute(expression="15 / 3")
        assert result.success is True
        assert result.result == 5.0
    
    def test_complex_expressions(self, calculator):
        """Test complex mathematical expressions"""
        # Order of operations
        result = calculator.execute(expression="2 + 3 * 4")
        assert result.success is True
        assert result.result == 14
        
        # Parentheses
        result = calculator.execute(expression="(2 + 3) * 4")
        assert result.success is True
        assert result.result == 20
        
        # Power operation
        result = calculator.execute(expression="2 ** 3")
        assert result.success is True
        assert result.result == 8
        
        # Modulo
        result = calculator.execute(expression="17 % 5")
        assert result.success is True
        assert result.result == 2
    
    def test_mathematical_functions(self, calculator):
        """Test mathematical functions"""
        # Square root
        result = calculator.execute(expression="sqrt(16)")
        assert result.success is True
        assert result.result == 4.0
        
        # Sine (approximately)
        result = calculator.execute(expression="sin(0)")
        assert result.success is True
        assert abs(result.result - 0) < 1e-10
        
        # Cosine
        result = calculator.execute(expression="cos(0)")
        assert result.success is True
        assert abs(result.result - 1) < 1e-10
        
        # Natural logarithm
        result = calculator.execute(expression="log(math.e)")
        assert result.success is True
        assert abs(result.result - 1) < 1e-10
        
        # Exponential
        result = calculator.execute(expression="exp(0)")
        assert result.success is True
        assert abs(result.result - 1) < 1e-10
    
    def test_error_handling(self, calculator):
        """Test error handling for invalid expressions"""
        # Division by zero
        result = calculator.execute(expression="1 / 0")
        assert result.success is False
        assert "error" in result.error.lower()
        
        # Invalid syntax
        result = calculator.execute(expression="2 +")
        assert result.success is False
        assert result.error is not None
        
        # Invalid function
        result = calculator.execute(expression="invalid_function(5)")
        assert result.success is False
        assert result.error is not None
    
    def test_floating_point_results(self, calculator):
        """Test floating point calculations"""
        result = calculator.execute(expression="7 / 3")
        assert result.success is True
        assert abs(result.result - 2.333333333333333) < 1e-10
        
        result = calculator.execute(expression="sqrt(2)")
        assert result.success is True
        assert abs(result.result - math.sqrt(2)) < 1e-10
    
    def test_tool_definition(self, calculator):
        """Test tool definition structure"""
        definition = calculator.get_tool_definition()
        
        assert isinstance(definition, ToolDefinition)
        assert definition.type == "function"
        assert definition.function["name"] == "calculator"
        assert definition.function["description"] == "Perform mathematical calculations"
        
        # Check parameters structure
        params = definition.function["parameters"]
        assert params["type"] == "object"
        assert "expression" in params["properties"]
        assert params["properties"]["expression"]["type"] == "string"
        assert "expression" in params["required"]
    
    def test_edge_cases(self, calculator):
        """Test edge cases"""
        # Very large numbers
        result = calculator.execute(expression="10**100")
        assert result.success is True
        assert result.result == 10**100
        
        # Very small numbers
        result = calculator.execute(expression="1e-10")
        assert result.success is True
        assert result.result == 1e-10
        
        # Negative numbers
        result = calculator.execute(expression="-5 + 3")
        assert result.success is True
        assert result.result == -2
    
    def test_trigonometric_functions(self, calculator):
        """Test trigonometric functions"""
        # Test with pi/2
        result = calculator.execute(expression="sin(math.pi/2)")
        assert result.success is True
        assert abs(result.result - 1) < 1e-10
        
        result = calculator.execute(expression="cos(math.pi)")
        assert result.success is True
        assert abs(result.result - (-1)) < 1e-10
        
        result = calculator.execute(expression="tan(math.pi/4)")
        assert result.success is True
        assert abs(result.result - 1) < 1e-10
    
    def test_absolute_and_rounding(self, calculator):
        """Test absolute value and rounding functions"""
        # Absolute value
        result = calculator.execute(expression="abs(-42)")
        assert result.success is True
        assert result.result == 42
        
        # Rounding
        result = calculator.execute(expression="round(3.14159, 2)")
        assert result.success is True
        assert result.result == 3.14