# Random Python Code Generator
import random
import math
from datetime import datetime
import unittest
from python_code_parser import analyze_code

class DataProcessor:
    """This class processes various types of data."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.temp_data = []
        self.MAX_ITEMS = 100
        
    def process_numbers(self, nums):
        """Process a list of numbers and return statistics."""
        if not nums:
            return None
            
        total = sum(nums)
        avg = total / len(nums)
        squared = [x**2 for x in nums]
        
        # 处理数字并返回结果
        return {
            'sum': total,
            'average': avg,
            'squared_values': squared
        }
        
    def filter_data(self, predicate):
        """Filter temp_data using the given predicate function."""
        return [x for x in self.temp_data if predicate(x)]
        
    @staticmethod
    def current_time():
        """返回当前时间戳"""
        return datetime.now().isoformat()

def calculate_area(radius):
    """Calculate the area of a circle."""
    return math.pi * (radius ** 2)

# 全局变量
GLOBAL_CONST = 3.14159
user_names = ['Alice', 'Bob', 'Charlie']

def main():
    """Main entry point for the application."""
    processor = DataProcessor({'debug': True})
    numbers = [random.randint(1, 100) for _ in range(10)]
    
    # 处理数字
    result = processor.process_numbers(numbers)
    print(f"Result: {result}")
    
    # 计算圆的面积
    r = 5.0
    area = calculate_area(r)
    print(f"Area of circle with radius {r} is {area:.2f}")
    
    # 打印当前时间
    print(f"Current time: {DataProcessor.current_time()}")
    
    # 日本語のコメント (Japanese comment)
    if GLOBAL_CONST > 3:
        print("PI is greater than 3")

class TestParserAccuracy(unittest.TestCase):
    def test_simple_file(self):
        # Test case 1: Basic Python file with known quantities
        code = """# This is a comment (1)
x = 5  # Constant (1)

def foo():  # Function (1)
    \"\"\"Docstring (1)\"\"\"
    y = "hello"  # Literal (1), identifier (1)
    
class Bar:  # Class (1)
    pass
"""
        
        result = analyze_code(code)
        result_dict = result.to_dict()
        
        # Test counts
        self.assertEqual(result.function_count, 1, "Should find 1 function")
        self.assertEqual(result.class_count, 1, "Should find 1 class")
        self.assertEqual(result.docstring_count, 1, "Should find 1 docstring")
        self.assertEqual(result.variable_count, 2, "Should find 2 variables (x, y)")
        self.assertEqual(result.comment_count, 2, "Should find 2 comments")
        self.assertEqual(result.non_english_count, 0, "Should find no non-English content")
        
        # Test specific instances
        self.assertIn("foo", result.function_names, "Should find function 'foo'")
        self.assertIn("Bar", result.class_names, "Should find class 'Bar'")
        self.assertIn("x", result.variables, "Should find variable 'x'")
        self.assertIn("y", result.variables, "Should find variable 'y'")
    
    def test_non_english_content(self):
        # Test case 2: Edge cases and special syntax
        code = '''# Comment with non-English: こんにちは
变量1 = 3.14  # Variable with Chinese name

def 函数1():  # Function with Chinese name
    """Docstring with Japanese: さようなら"""
    return f"Hello {变量1}"
'''
        
        result = analyze_code(code)
        result_dict = result.to_dict()
        
        # Test counts
        self.assertEqual(result.function_count, 1, "Should find 1 function")
        self.assertEqual(result.variable_count, 1, "Should find 1 variable")
        self.assertEqual(result.docstring_count, 1, "Should find 1 docstring")
        self.assertTrue(result.non_english_count >= 3, "Should find at least 3 non-English items")
        
        # Test specific instances
        self.assertIn("变量1", result.variables, "Should find Chinese variable name")
        self.assertIn("函数1", result.function_names, "Should find Chinese function name")
        self.assertIn("こんにちは", result.non_english, "Should find Japanese in comment")

if __name__ == '__main__':
    unittest.main()