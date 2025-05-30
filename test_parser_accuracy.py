import unittest
from python_code_parser import analyze_code
import json
from collections import defaultdict

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

def test_accuracy():
    # Test cases with known correct outputs
    test_cases = {
        # Japanese test case
        "japanese_test": {
            "code": '''
# 日本語テスト
class テストクラス:
    def テスト関数(self):
        変数 = "こんにちは"
        CONSTANT_値 = 42
        return 変数
''',
            "expected": {
                "class_names": ["テストクラス"],
                "function_names": ["テスト関数"],
                "variables": ["変数"],
                "constants": ["CONSTANT_値"],
                "literals": ["こんにちは"],
                "language": "Japanese"
            }
        },
        # Chinese test case
        "chinese_test": {
            "code": '''
# 中文测试
class 测试类:
    def 测试函数(self):
        变量 = "你好"
        CONSTANT_值 = 42
        return 变量
''',
            "expected": {
                "class_names": ["测试类"],
                "function_names": ["测试函数"],
                "variables": ["变量"],
                "constants": ["CONSTANT_值"],
                "literals": ["你好"],
                "language": "Chinese"
            }
        },
        # Mixed script test case
        "mixed_test": {
            "code": '''
def process_data(データ: List[str]) -> Dict[str, Any]:
    """
    Process mixed language data
    データを処理する
    处理数据
    """
    result = {}
    for item in データ:
        if "テスト" in item:
            result["test"] = True
        elif "测试" in item:
            result["test"] = False
    return result
''',
            "expected": {
                "function_names": ["process_data"],
                "variables": ["データ"],
                "docstrings": ["Process mixed language data\nデータを処理する\n处理数据"],
                "mixed_scripts": True
            }
        },
        # Emoji test case
        "emoji_test": {
            "code": '''
def analyze_trend(data) -> str:
    """Analyze trend 📈"""
    if data > 0:
        return "Up 📈"
    return "Down 📉"
''',
            "expected": {
                "contains_emoji": True,
                "emoji_count": 3
            }
        }
    }

    scores = defaultdict(list)
    
    def calculate_match_score(found, expected):
        if not expected:
            return 100 if not found else 0
        matches = sum(1 for item in found if item in expected)
        total = max(len(found), len(expected))
        return (matches / total) * 100 if total > 0 else 100

    print("=== Parser Accuracy Test ===\n")
    
    for test_name, test_case in test_cases.items():
        print(f"Testing {test_name}...")
        result = analyze_code(test_case["code"])
        expected = test_case["expected"]
        
        # Test different aspects
        if "class_names" in expected:
            score = calculate_match_score(result.class_names, set(expected["class_names"]))
            scores["class_detection"].append(score)
            print(f"  Class Detection: {score:.1f}%")
            
        if "function_names" in expected:
            score = calculate_match_score(result.function_names, set(expected["function_names"]))
            scores["function_detection"].append(score)
            print(f"  Function Detection: {score:.1f}%")
            
        if "variables" in expected:
            score = calculate_match_score(result.variables, set(expected["variables"]))
            scores["variable_detection"].append(score)
            print(f"  Variable Detection: {score:.1f}%")
            
        if "constants" in expected:
            score = calculate_match_score(result.constants, set(expected["constants"]))
            scores["constant_detection"].append(score)
            print(f"  Constant Detection: {score:.1f}%")
            
        if "literals" in expected:
            score = calculate_match_score(result.literals, set(expected["literals"]))
            scores["literal_detection"].append(score)
            print(f"  Literal Detection: {score:.1f}%")
            
        if "docstrings" in expected:
            score = calculate_match_score(result.docstrings, set(expected["docstrings"]))
            scores["docstring_detection"].append(score)
            print(f"  Docstring Detection: {score:.1f}%")
            
        if "contains_emoji" in expected:
            has_emoji = any("📈" in item or "📉" in item for item in result.literals)
            score = 100 if has_emoji == expected["contains_emoji"] else 0
            scores["emoji_detection"].append(score)
            print(f"  Emoji Detection: {score:.1f}%")
            
        print()

    # Calculate overall accuracy
    category_scores = {
        "Class Detection": sum(scores["class_detection"]) / len(scores["class_detection"]) if scores["class_detection"] else 0,
        "Function Detection": sum(scores["function_detection"]) / len(scores["function_detection"]) if scores["function_detection"] else 0,
        "Variable Detection": sum(scores["variable_detection"]) / len(scores["variable_detection"]) if scores["variable_detection"] else 0,
        "Constant Detection": sum(scores["constant_detection"]) / len(scores["constant_detection"]) if scores["constant_detection"] else 0,
        "Literal Detection": sum(scores["literal_detection"]) / len(scores["literal_detection"]) if scores["literal_detection"] else 0,
        "Docstring Detection": sum(scores["docstring_detection"]) / len(scores["docstring_detection"]) if scores["docstring_detection"] else 0,
        "Emoji Detection": sum(scores["emoji_detection"]) / len(scores["emoji_detection"]) if scores["emoji_detection"] else 0
    }
    
    print("=== Overall Accuracy ===")
    total_score = 0
    for category, score in category_scores.items():
        print(f"{category}: {score:.1f}%")
        total_score += score
        
    final_score = total_score / len(category_scores)
    print(f"\nFinal Accuracy Score: {final_score:.1f}/100")

if __name__ == '__main__':
    unittest.main(verbosity=2)
    test_accuracy() 