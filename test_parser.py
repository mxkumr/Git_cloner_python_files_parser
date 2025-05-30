from python_code_parser import analyze_file
import json
from pprint import pprint

def print_section(title, items):
    print(f"\n{title}:")
    if isinstance(items, (set, list)):
        for item in sorted(items):
            print(f"  - {item}")
    else:
        print(f"  {items}")

def test_parser():
    # Analyze the test file
    result = analyze_file('test_non_english.py')
    
    # Convert to dictionary for easier access
    data = result.to_dict()
    
    print("=== Non-English Content Analysis ===")
    
    # Print counts
    print("\nCounts:")
    counts = data['counts']
    print(f"  Non-English identifiers: {counts['non_english_identifier_count']}")
    print(f"  Non-English literals: {counts['non_english_literal_count']}")
    print(f"  Non-English class names: {counts['non_english_class_count']}")
    print(f"  Non-English function names: {counts['non_english_function_count']}")
    print(f"  Non-English variables: {counts['non_english_variable_count']}")
    print(f"  Non-English docstrings: {counts['non_english_docstring_count']}")
    print(f"  Non-English constants: {counts['non_english_constant_count']}")
    print(f"  Non-English comments: {counts['non_english_comment_count']}")
    
    # Print instances
    instances = data['instances']
    print_section("Non-English Identifiers", instances['non_english_identifiers'])
    print_section("Non-English Literals", instances['non_english_literals'])
    print_section("Non-English Class Names", instances['non_english_class_names'])
    print_section("Non-English Function Names", instances['non_english_function_names'])
    print_section("Non-English Variables", instances['non_english_variables'])
    print_section("Non-English Docstrings", instances['non_english_docstrings'])
    print_section("Non-English Constants", instances['non_english_constants'])
    print_section("Non-English Comments", instances['non_english_comments'])

if __name__ == '__main__':
    test_parser() 