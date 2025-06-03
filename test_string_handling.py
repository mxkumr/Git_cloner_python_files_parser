import unittest
from python_code_parser import analyze_code, is_non_english, detect_languages_in_text

class TestStringHandling(unittest.TestCase):
    def test_empty_strings(self):
        code = '''
# Test empty strings and whitespace
empty = ""
whitespace = "   "
empty_multiline = """
"""
mixed_content = "Hello 你好"  # Mixed English and Chinese
only_symbols = "!@#$%^"
only_spaces = "     "
chinese_word = "世界"  # Single Chinese word
empty_list = ["", "  ", "", "hello", "", "世界", ""]

# Test string assignments
s1 = ""
s2 = "   "
s3 = """"""
s4 = " "
'''
        result = analyze_code(code)
        
        # Debug information
        print("\nTest Results:")
        print("Literals:", result.literals)
        print("Non-English literals:", result.non_english_literals)
        
        # Test is_non_english function directly
        print("\nTesting is_non_english function:")
        test_strings = ["", "   ", " ", "Hello 你好", "世界"]
        for s in test_strings:
            print(f"is_non_english('{s}') = {is_non_english(s)}")
            print(f"detect_languages_in_text('{s}') = {detect_languages_in_text(s)}")
        
        # Verify empty strings are not in non_english_literals
        self.assertNotIn("", result.non_english_literals)
        self.assertNotIn("   ", result.non_english_literals)
        self.assertNotIn(" ", result.non_english_literals)
        
        # Verify that non-English content is still detected
        self.assertIn("你好", result.non_english_literals)
        self.assertIn("世界", result.non_english_literals)
        
        # Verify empty strings are not counted as non-English
        self.assertGreater(len(result.literals), len(result.non_english_literals))

    def test_english_detection(self):
        code = '''
# Test English and programming terms
api_call = "API"
row_data = "Head Row"
args_test = "__args__[1]"
comments = [
    "#   Head  Row.",
    "#    .",
    "# Row        __args__[0] .",
    "#   Head  Row."
]
programming_terms = {
    "API": "Application Programming Interface",
    "URL": "http://example.com",
    "SQL": "SELECT * FROM table",
    "HTML": "<div>content</div>"
}
'''
        result = analyze_code(code)
        
        print("\nEnglish Detection Results:")
        print("Comments:", result.comments)
        print("Non-English comments:", result.non_english_comments)
        print("Literals:", result.literals)
        print("Non-English literals:", result.non_english_literals)
        
        # Verify English terms are not marked as non-English
        self.assertNotIn("API", result.non_english_literals)
        self.assertNotIn("#   Head  Row.", result.non_english_comments)
        self.assertNotIn("__args__[1]", result.non_english_literals)
        
        # Test common programming terms
        test_terms = ["API", "URL", "SQL", "HTML", "__args__[1]", "Head Row"]
        for term in test_terms:
            self.assertFalse(is_non_english(term), f"'{term}' was incorrectly marked as non-English")

if __name__ == '__main__':
    unittest.main() 