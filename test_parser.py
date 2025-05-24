from python_code_parser import analyze_code

# Test code with various non-English content
test_code = '''
def 测试函数():  # Chinese function name
    # 这是一个测试 - Chinese comment
    名字 = "张三"  # Chinese variable and string
    print("こんにちは")  # Japanese string
    # مرحبا - Arabic comment
    변수 = "안녕하세요"  # Korean variable and string
    
    # Mixed content
    user_name = "李明"  # English variable, Chinese string
    greeting = "Bonjour, 世界!"  # French and Chinese mixed
    
    # Test with numbers and symbols
    price = 123.45  # Should be ignored
    symbols = "!@#$%"  # Should be ignored
'''

# Run the analysis
result = analyze_code(test_code)

# Print results in a formatted way
print("\n=== Analysis Results ===")
print("\nNon-English Content:")
for item in result.non_english:
    print(f"  - {item}")

print("\nIdentifiers:")
for item in result.identifiers:
    print(f"  - {item}")

print("\nComments:")
for item in result.comments:
    print(f"  - {item}")

print("\nString Literals:")
for item in result.literals:
    print(f"  - {item}")

print("\nStatistics:")
print(f"  Non-English items: {result.non_english_count}")
print(f"  Total identifiers: {result.identifier_count}")
print(f"  Total comments: {result.comment_count}")
print(f"  Total literals: {result.literal_count}")
print(f"  Total constants: {result.constant_count}")
print(f"  Total keywords: {result.keyword_count}") 