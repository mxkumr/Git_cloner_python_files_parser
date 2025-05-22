from typing import NamedTuple, Set
import ast
import unicodedata
from langdetect import detect, LangDetectException
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseResult(NamedTuple):
    """Results from parsing a Python file"""
    keywords: Set[str]
    identifiers: Set[str]
    literals: Set[str]
    constants: Set[str]
    comments: Set[str]
    non_english: Set[str]
    keyword_count: int
    identifier_count: int
    literal_count: int
    constant_count: int
    comment_count: int
    non_english_count: int

def is_english_word(text: str) -> bool:
    """
    Check if a word appears to be English.
    Returns True if the word contains only ASCII letters, numbers, and common punctuation.
    """
    # Remove common programming symbols and numbers
    text = re.sub(r'[0-9_\-\.:]', '', text)
    
    # If nothing left after removing symbols, consider it English
    if not text:
        return True
        
    # Check if remaining text contains only ASCII letters
    return all(ord(c) < 128 for c in text)

def detect_specific_language(text: str) -> str:
    """
    Detect specific language of the text.
    Returns normalized language code or 'unknown' if detection fails.
    Common language codes:
    - 'zh': Chinese (including zh-cn, zh-tw)
    - 'ar': Arabic
    - 'ja': Japanese
    - 'ko': Korean
    - 'ru': Russian
    - 'hi': Hindi
    etc.
    """
    try:
        if not text or len(text.strip()) < 3:
            return 'unknown'
        # Skip if text contains only ASCII characters
        if all(ord(c) < 128 for c in text):
            return 'en'
        
        lang = detect(text)
        
        # Normalize language codes
        if lang.startswith('zh-'):
            return 'zh'
        elif lang == 'bg':  # Bulgarian often confused with Russian
            return 'ru'
        return lang
        
    except Exception:
        return 'unknown'

def is_non_english(text: str) -> bool:
    """
    Check if text contains non-English content by detecting specific languages.
    Returns True if text contains characters in languages like Chinese, Arabic, etc.
    """
    # Skip empty strings
    if not text:
        return False
        
    # Skip strings that are just numbers, symbols, or whitespace
    if re.match(r'^[\d\s\W_]*$', text):
        return False
        
    # Remove comment markers and common punctuation
    text = text.strip('# ')
    text = re.sub(r'[!@#$%^&*(),.?":{}|<>]', '', text)
    
    # Split into words and handle compound strings
    words = []
    current_word = ''
    
    for char in text:
        if char.isspace():
            if current_word:
                words.append(current_word)
                current_word = ''
        else:
            # Start a new word if switching between ASCII and non-ASCII
            if current_word and ((ord(char) > 127) != (ord(current_word[-1]) > 127)):
                words.append(current_word)
                current_word = ''
            current_word += char
    
    if current_word:
        words.append(current_word)
    
    # If no words found, it's not non-English
    if not words:
        return False
        
    # Check each word
    non_english_words = []
    for word in words:
        # Skip common programming terms
        if word.lower() in {'str', 'int', 'dict', 'list', 'set', 'bool', 'none', 'true', 'false'}:
            continue
            
        # First check for non-ASCII characters
        if any(ord(c) > 127 for c in word):
            # Then try to detect specific language
            lang = detect_specific_language(word)
            if lang not in {'en', 'unknown'}:
                non_english_words.append(word)
    
    # If we found any non-English words, return True
    return len(non_english_words) > 0

def detect_language(text: str) -> str:
    """
    Detect the language of the given text using langdetect.
    Returns language code or 'unknown' if detection fails.
    """
    try:
        if not text or len(text.strip()) < 3:
            return 'unknown'
        return detect(text)
    except LangDetectException:
        return 'unknown'

class PythonAstVisitor(ast.NodeVisitor):
    def __init__(self):
        self.keywords = set()
        self.identifiers = set()
        self.literals = set()
        self.constants = set()
        self.comments = set()
        self.non_english = set()

    def visit_Name(self, node):
        """Handle variable and function names"""
        name = node.id
        self.identifiers.add(name)
        if is_non_english(name):
            # For identifiers, store the exact name
            self.non_english.add(name)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Handle class attributes (e.g., self.名前)"""
        attr_name = node.attr
        self.identifiers.add(attr_name)
        if is_non_english(attr_name):
            self.non_english.add(attr_name)
        self.generic_visit(node)

    def visit_Str(self, node):
        """Handle string literals"""
        value = node.s
        self.literals.add(value)
        if is_non_english(value):
            # For strings, split and store non-English parts
            for word in re.findall(r'[^\s!@#$%^&*(),.?":{}|<>]+', value):
                if any(ord(c) > 127 for c in word):
                    self.non_english.add(word)
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Handle constants (Python 3.8+)"""
        if isinstance(node.value, str):
            self.literals.add(node.value)
            if is_non_english(node.value):
                # For strings, split and store non-English parts
                for word in re.findall(r'[^\s!@#$%^&*(),.?":{}|<>]+', node.value):
                    if any(ord(c) > 127 for c in word):
                        self.non_english.add(word)
        elif isinstance(node.value, (int, float, bool, type(None))):
            self.constants.add(str(node.value))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Handle function names"""
        name = node.name
        self.identifiers.add(name)
        if is_non_english(name):
            self.non_english.add(name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Handle class names"""
        name = node.name
        self.identifiers.add(name)
        if is_non_english(name):
            self.non_english.add(name)
        self.generic_visit(node)

def extract_comments(source_lines):
    """Extract comments from source code"""
    comments = set()
    non_english_comments = set()
    
    in_multiline = False
    multiline_content = []
    
    for line in source_lines:
        line = line.strip()
        
        # Handle multiline strings/comments
        if line.startswith('"""') or line.startswith("'''"):
            if not in_multiline:
                in_multiline = True
                multiline_content = [line.strip('"\'')] # Remove quotes
            else:
                in_multiline = False
                multiline_content.append(line.strip('"\''))
                comment = '\n'.join(multiline_content)
                comments.add(comment)
                if is_non_english(comment):
                    # Remove comment markers and clean up
                    clean_comment = comment.strip('# ')
                    non_english_comments.add(clean_comment)
                multiline_content = []
        elif in_multiline:
            multiline_content.append(line)
        else:
            # Handle single-line comments
            hash_pos = line.find('#')
            if hash_pos != -1:
                comment = line[hash_pos:].strip()
                comments.add(comment)
                if is_non_english(comment):
                    # Remove comment markers and clean up
                    clean_comment = comment.strip('# ')
                    non_english_comments.add(clean_comment)
    
    return comments, non_english_comments

def analyze_code(code: str) -> ParseResult:
    """
    Analyze Python code and extract various components including non-English content.
    
    Args:
        code: Python source code as string
        
    Returns:
        ParseResult containing sets of different code components and their counts
    """
    # Parse the AST
    tree = ast.parse(code)
    visitor = PythonAstVisitor()
    visitor.visit(tree)
    
    # Extract comments
    source_lines = code.splitlines()
    comments, non_english_comments = extract_comments(source_lines)
    
    # Combine results
    all_non_english = visitor.non_english | non_english_comments
    
    return ParseResult(
        keywords=visitor.keywords,
        identifiers=visitor.identifiers,
        literals=visitor.literals,
        constants=visitor.constants,
        comments=comments,
        non_english=all_non_english,
        keyword_count=len(visitor.keywords),
        identifier_count=len(visitor.identifiers),
        literal_count=len(visitor.literals),
        constant_count=len(visitor.constants),
        comment_count=len(comments),
        non_english_count=len(all_non_english)
    )

def analyze_file(file_path: str) -> ParseResult:
    """Analyze a Python file and return parsing results"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return analyze_code(content)
