# Python Code Parser for Non-English Content Analysis

This library provides tools to analyze Python code for non-English content in identifiers, comments, and string literals. It uses tree-sitter for robust parsing and langdetect for language detection.

## Features

- Extracts and analyzes:
  - Identifiers (variable/function names)
  - Comments (inline, docstrings)
  - String literals
  - Keywords
  - Constants
- Detects non-English content using Unicode analysis
- Provides language detection for text content
- Returns detailed statistics about code components

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. The library will automatically set up tree-sitter and its Python grammar on first use.

## Usage

```python
from python_code_parser import analyze_code, analyze_file

# Analyze code string
code = '''
def 你好():  # Chinese function name
    print("こんにちは")  # Japanese string literal
    # Arabic comment مرحبا
    世界 = "Hello"  # Chinese variable name
'''

result = analyze_code(code)

# Access the results
print("Non-English content:", result.non_english)
print("Identifiers:", result.identifiers)
print("Comments:", result.comments)
print("String literals:", result.literals)

# Or analyze a file directly
result = analyze_file("your_python_file.py")
```

## ParseResult Structure

The analysis returns a `ParseResult` named tuple with the following fields:

- `keywords`: Set of Python keywords used
- `identifiers`: Set of variable/function names
- `literals`: Set of string literals
- `constants`: Set of numeric/boolean constants
- `comments`: Set of comments
- `non_english`: Set of detected non-English content
- `*_count`: Count fields for each category above

## Language Detection

The library uses two approaches for detecting non-English content:

1. Unicode analysis: Checks if characters are outside the basic Latin alphabet
2. Language detection: Uses the `langdetect` library to identify specific languages

## Contributing

Feel free to open issues or submit pull requests for improvements! 