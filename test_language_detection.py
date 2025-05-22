import unittest
from python_code_parser import analyze_code, detect_specific_language

class TestLanguageDetection(unittest.TestCase):
    def test_mixed_language_code(self):
        code = '''
# This is a test file with multiple languages
def calculate_sum(numbers):
    # 计算总和
    total = 0
    # مجموع
    for num in numbers:
        total += num
    return total

class Student:
    def __init__(self):
        self.名前 = ""  # Japanese variable
        self.학생 = ""   # Korean variable
        self.طالب = ""   # Arabic variable

# Test string literals
messages = {
    "chinese": "你好，世界",
    "japanese": "こんにちは",
    "korean": "안녕하세요",
    "arabic": "مرحبا",
    "russian": "Привет",
    "hindi": "नमस्ते",
    "english": "Hello World"
}
'''
        result = analyze_code(code)
        print("\nAnalysis Results:")
        print(f"Total non-English items found: {result.non_english_count}")
        print("\nNon-English content:")
        for item in result.non_english:
            lang = detect_specific_language(item)
            print(f"'{item}' - Detected as: {lang}")
        
        # Verify we found non-English content
        self.assertTrue(len(result.non_english) > 0)
        
        # Verify specific languages were detected
        chinese_found = any(detect_specific_language(item) == 'zh' for item in result.non_english)
        arabic_found = any(detect_specific_language(item) == 'ar' for item in result.non_english)
        japanese_found = any(detect_specific_language(item) == 'ja' for item in result.non_english)
        korean_found = any(detect_specific_language(item) == 'ko' for item in result.non_english)
        
        self.assertTrue(chinese_found, "Chinese text not detected")
        self.assertTrue(arabic_found, "Arabic text not detected")
        self.assertTrue(japanese_found, "Japanese text not detected")
        self.assertTrue(korean_found, "Korean text not detected")

    def test_english_only(self):
        code = '''
def hello_world():
    print("Hello World!")
    return True
'''
        result = analyze_code(code)
        self.assertEqual(len(result.non_english), 0, "English-only code was flagged as non-English")

if __name__ == '__main__':
    unittest.main() 