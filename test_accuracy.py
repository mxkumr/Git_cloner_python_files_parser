from python_code_parser import analyze_code

def test_parser_accuracy():
    # Test cases with known correct outputs
    test_code = '''
# 多语言测试文件 - Multilingual Test File - マルチ言語テスト
class 基本クラス:
    """Base class for testing"""
    def __init__(self):
        self.变量 = "测试"
        self.テスト = "テスト"
        self.КОНСТАНТА = "Привет"
        
    def процесс(self):
        """Russian method"""
        return "Выполнено"
        
    def テスト関数(self):
        """Japanese method"""
        return "完了"
        
    def 处理(self):
        """Chinese method"""
        return "完成"

def main():
    # Emoji test
    status = "Success 📈"
    error = "Failed 📉"
    
    # Extended Latin
    résumé = "Café"
    
    # Mixed scripts
    data = {
        "jp": "こんにちは",
        "cn": "你好",
        "kr": "안녕하세요",
        "ru": "Привет",
        "ar": "مرحبا",
        "th": "สวัสดี"
    }
    
    # Constants
    MAX_サイズ = 100
    MIN_크기 = 0
    
    return "Done! ✅"
'''

    result = analyze_code(test_code)
    scores = {}
    
    # Test language detection accuracy
    expected_languages = {
        'Japanese': ['テスト', 'テスト関数', '完了', 'こんにちは', 'サイズ'],
        'Chinese': ['变量', '测试', '处理', '完成', '你好'],
        'Korean': ['안녕하세요', '크기'],
        'Russian': ['КОНСТАНТА', 'Привет', 'процесс', 'Выполнено'],
        'Arabic': ['مرحبا'],
        'Thai': ['สวัสดี'],
        'Extended_Latin': ['résumé', 'Café'],
        'Emoji': ['📈', '📉', '✅']
    }
    
    detected_count = 0
    total_items = 0
    
    print("=== Language Detection Accuracy ===")
    for lang, items in expected_languages.items():
        found = 0
        for item in items:
            if any(item in s for s in result.non_english):
                found += 1
        accuracy = (found / len(items)) * 100
        print(f"{lang}: {accuracy:.1f}% ({found}/{len(items)} items detected)")
        detected_count += found
        total_items += len(items)
    
    language_detection_score = (detected_count / total_items) * 100
    scores['Language Detection'] = language_detection_score
    
    # Test code element categorization
    expected_elements = {
        'class_names': ['基本クラス'],
        'function_names': ['процесс', 'テスト関数', '处理'],
        'variables': ['变量', 'テスト', 'КОНСТАНТА', 'résumé', 'サイズ', '크기'],
        'constants': ['MAX_サイズ', 'MIN_크기'],
        'docstrings': ['Russian method', 'Japanese method', 'Chinese method']
    }
    
    print("\n=== Code Element Categorization Accuracy ===")
    for category, expected in expected_elements.items():
        actual = getattr(result, category)
        found = sum(1 for item in expected if any(item in s for s in actual))
        accuracy = (found / len(expected)) * 100
        print(f"{category}: {accuracy:.1f}% ({found}/{len(expected)} items detected)")
        scores[category] = accuracy
    
    # Calculate final score
    final_score = sum(scores.values()) / len(scores)
    print(f"\nFinal Parser Accuracy Score: {final_score:.1f}/100")
    
    # Detailed breakdown
    print("\nDetailed Score Breakdown:")
    for category, score in scores.items():
        print(f"{category}: {score:.1f}")

if __name__ == "__main__":
    test_parser_accuracy() 