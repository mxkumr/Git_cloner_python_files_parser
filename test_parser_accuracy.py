import unittest
from python_code_parser import analyze_code

class TestParserAccuracy(unittest.TestCase):
    def test_comprehensive_code_analysis(self):
        # Test code with various Python constructs
        test_code = '''
"""
Module level docstring.
This is a test module for checking parser accuracy.
"""

import os
import json as json_lib
from datetime import datetime

# Global variables
GLOBAL_CONSTANT = 100
你好_variable = "Hello in Chinese"
αβ_greek = "Greek letters"

class TestClass:
    """
    Test class docstring.
    Contains various test methods and attributes.
    """
    
    class_var = "Class variable"
    
    def __init__(self, name: str):
        """Constructor docstring."""
        self.name = name
        self.名前 = "Japanese name"  # Non-English variable
    
    def test_method(self) -> None:
        """Test method docstring."""
        # Local variables
        local_var = 42
        mixed_var_名前 = "Mixed"
        
        # Test literals
        numbers = [1, 2, 3]
        strings = ["abc", "def"]
        
        # Test non-English strings
        messages = {
            "cn": "你好，世界",  # Chinese
            "jp": "こんにちは",  # Japanese
            "kr": "안녕하세요",  # Korean
            "ar": "مرحبا"      # Arabic
        }
        
        # Test module attributes
        path = os.path.join("a", "b")
        current_time = datetime.now()
        json_str = json_lib.dumps({"key": "value"})

def standalone_function(param1: str, param2: int = 0) -> str:
    """
    Standalone function docstring.
    Tests function definition parsing.
    
    Args:
        param1: First parameter
        param2: Second parameter with default
    
    Returns:
        A string result
    """
    result = f"{param1}: {param2}"
    return result

# Test function with non-English name
def 테스트_함수():
    """Korean function name test."""
    pass

# More test cases
async def async_function():
    """Async function test."""
    await_var = "test"
    return await_var

class ChildClass(TestClass):
    """Child class for inheritance testing."""
    def inherited_method(self):
        super().test_method()
'''
        
        # Analyze the test code
        result = analyze_code(test_code)
        
        # Print detailed results for debugging
        print("\n=== Parser Analysis Results ===")
        print(f"Functions ({result.function_count}):", sorted(result.function_names))
        print(f"Classes ({result.class_count}):", sorted(result.class_names))
        print(f"Variables ({result.variable_count}):", sorted(result.variables))
        print(f"Module Attributes:", sorted(result.module_attrs))
        print(f"Docstrings ({result.docstring_count}):", [d[:50] + "..." for d in result.docstrings])
        print(f"Non-English ({result.non_english_count}):", sorted(result.non_english))
        
        # Test function detection
        self.assertIn("standalone_function", result.function_names)
        self.assertIn("async_function", result.function_names)
        self.assertIn("테스트_함수", result.function_names)
        self.assertIn("test_method", result.function_names)
        
        # Test class detection
        self.assertIn("TestClass", result.class_names)
        self.assertIn("ChildClass", result.class_names)
        
        # Test variable detection
        self.assertIn("GLOBAL_CONSTANT", result.variables)
        self.assertIn("你好_variable", result.variables)
        self.assertIn("αβ_greek", result.variables)
        self.assertIn("class_var", result.variables)
        self.assertIn("local_var", result.variables)
        self.assertIn("mixed_var_名前", result.variables)
        
        # Test module attribute detection
        self.assertIn("os.path.join", result.module_attrs)
        self.assertIn("datetime.now", result.module_attrs)
        self.assertIn("json_lib.dumps", result.module_attrs)
        
        # Test docstring detection
        docstring_texts = [d.split('\n')[0].strip() for d in result.docstrings]
        self.assertIn("Module level docstring.", docstring_texts)
        self.assertIn("Test class docstring.", docstring_texts)
        self.assertIn("Constructor docstring.", docstring_texts)
        self.assertIn("Test method docstring.", docstring_texts)
        self.assertIn("Standalone function docstring.", docstring_texts)
        
        # Test non-English content detection
        self.assertIn("你好_variable", result.non_english)
        self.assertIn("名前", result.non_english)
        self.assertIn("테스트_함수", result.non_english)
        self.assertIn("你好，世界", result.non_english)
        self.assertIn("こんにちは", result.non_english)
        self.assertIn("안녕하세요", result.non_english)
        self.assertIn("مرحبا", result.non_english)

    def test_edge_cases(self):
        # Test empty code
        empty_result = analyze_code("")
        self.assertEqual(empty_result.function_count, 0)
        self.assertEqual(empty_result.class_count, 0)
        
        # Test code with only comments
        comment_code = """# Just a comment
# Another comment"""
        comment_result = analyze_code(comment_code)
        self.assertEqual(comment_result.function_count, 0)
        self.assertEqual(comment_result.comment_count, 2)
        
        # Test code with syntax errors
        invalid_code = "def invalid_func("
        with self.assertRaises(SyntaxError):
            analyze_code(invalid_code)

if __name__ == '__main__':
    unittest.main(verbosity=2) 