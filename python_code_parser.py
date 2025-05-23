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
    module_attrs: Set[str]  # Added to track module attributes
    function_names: Set[str]  # Added for function names
    class_names: Set[str]     # Added for class names
    variables: Set[str]       # Added for variables
    docstrings: Set[str]      # Added for docstrings
    keyword_count: int
    identifier_count: int
    literal_count: int
    constant_count: int
    comment_count: int
    non_english_count: int
    function_count: int       # Added count
    class_count: int         # Added count
    variable_count: int      # Added count
    docstring_count: int     # Added count

    def to_dict(self):
        """Convert ParseResult to a dictionary with both counts and actual instances"""
        return {
            'counts': {
                'keyword_count': self.keyword_count,
                'identifier_count': self.identifier_count,
                'literal_count': self.literal_count,
                'constant_count': self.constant_count,
                'comment_count': self.comment_count,
                'non_english_count': self.non_english_count,
                'function_count': self.function_count,
                'class_count': self.class_count,
                'variable_count': self.variable_count,
                'docstring_count': self.docstring_count
            },
            'instances': {
                'keywords': list(self.keywords),
                'identifiers': list(self.identifiers),
                'literals': list(self.literals),
                'constants': list(self.constants),
                'comments': list(self.comments),
                'non_english': list(self.non_english),
                'module_attrs': list(self.module_attrs),
                'function_names': list(self.function_names),
                'class_names': list(self.class_names),
                'variables': list(self.variables),
                'docstrings': list(self.docstrings)
            }
        }

def is_english_word(text: str) -> bool:
    """
    Check if a word appears to be English.
    Returns True if the word contains only ASCII letters, numbers, and common punctuation.
    """
    # Remove common programming symbols and numbers
    text = re.sub(r'[0-9_\-.:;]', '', text)
    
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
    text = re.sub(r'[!@#$%^&*()?":{}|<>]', '', text)
    
    # Check for non-ASCII characters directly in identifiers
    if any(ord(c) > 127 for c in text):
        return True
    
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
    return len(non_english_words) > 0 or any(ord(c) > 127 for c in text)

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
        self.imported_modules = set()  # Track imported modules
        self.module_attrs = set()      # Track module attributes/methods
        self.function_names = set()    # Track function names
        self.class_names = set()       # Track class names
        self.variables = set()         # Track variable names
        self.docstrings = set()        # Track docstrings

    def visit_Import(self, node):
        """Handle import statements"""
        for name in node.names:
            # Add the module name to both imported_modules and identifiers
            module_name = name.name.split('.')[0]  # Get the base module name
            asname = name.asname if name.asname else name.name
            self.imported_modules.add(asname)  # Use the alias if present
            self.identifiers.add(module_name)  # Add base module name to identifiers
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Handle from ... import statements"""
        if node.module:
            # Add the base module name to both imported_modules and identifiers
            module_name = node.module.split('.')[0]  # Get the base module name
            self.imported_modules.add(node.module)
            self.identifiers.add(module_name)  # Add base module name to identifiers
        for name in node.names:
            if node.module:
                self.module_attrs.add(f"{node.module}.{name.name}")
            else:
                self.module_attrs.add(name.name)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Handle class attributes and module attributes"""
        attr_name = node.attr
        # Build full attribute path
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            # Reverse to get correct order
            full_path = '.'.join(reversed(parts))
            base_module = parts[-1]  # The root module/object name
            
            # Check if it's a module attribute
            if base_module in self.imported_modules:
                self.module_attrs.add(full_path)
                return  # Skip adding to identifiers if it's a module attribute
            
            # If not a module attribute, process normally
            self.identifiers.add(attr_name)
            if is_non_english(attr_name):
                self.non_english.add(attr_name)
        self.generic_visit(node)

    def visit_Name(self, node):
        """Handle variable and function names"""
        name = node.id
        # Only add to identifiers if it's not a module or module attribute
        if name not in self.imported_modules and not any(name in attr for attr in self.module_attrs):
            # Check if it's being used in a way that suggests it's a variable
            if isinstance(node.ctx, (ast.Store, ast.AugStore)):
                self.variables.add(name)
                if is_non_english(name):
                    self.non_english.add(name)
            self.identifiers.add(name)
            if is_non_english(name):
                self.non_english.add(name)
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
        """Handle function definitions"""
        name = node.name
        self.function_names.add(name)
        self.identifiers.add(name)
        
        # Check for docstring
        if (ast.get_docstring(node)):
            self.docstrings.add(ast.get_docstring(node))
            
        if is_non_english(name):
            self.non_english.add(name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Handle async function definitions"""
        # Use the same logic as regular functions
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        """Handle class definitions"""
        name = node.name
        self.class_names.add(name)
        self.identifiers.add(name)
        
        # Check for docstring
        if (ast.get_docstring(node)):
            self.docstrings.add(ast.get_docstring(node))
            
        if is_non_english(name):
            self.non_english.add(name)
        self.generic_visit(node)

    def visit_Module(self, node):
        """Handle module-level docstrings"""
        if (ast.get_docstring(node)):
            self.docstrings.add(ast.get_docstring(node))
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Handle variable assignments"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                self.variables.add(name)
                if is_non_english(name):
                    self.non_english.add(name)
            elif isinstance(target, ast.Attribute):
                # Handle attribute assignments (e.g., self.name = value)
                attr_name = target.attr
                if is_non_english(attr_name):
                    self.non_english.add(attr_name)
        self.generic_visit(node)

def extract_comments(source_lines):
    """Extract comments from source code"""
    comments = set()
    non_english_comments = set()
    
    in_multiline = False
    multiline_content = []
    
    for i, line in enumerate(source_lines):
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
                if comment:  # Only add non-empty comments
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
    
    # Count actual comments (excluding empty lines and whitespace)
    actual_comments = {c for c in comments if c.strip()}
    
    return ParseResult(
        keywords=visitor.keywords,
        identifiers=visitor.identifiers,
        literals=visitor.literals,
        constants=visitor.constants,
        comments=actual_comments,
        non_english=all_non_english,
        module_attrs=visitor.module_attrs,
        function_names=visitor.function_names,
        class_names=visitor.class_names,
        variables=visitor.variables,
        docstrings=visitor.docstrings,
        keyword_count=len(visitor.keywords),
        identifier_count=len(visitor.identifiers),
        literal_count=len(visitor.literals),
        constant_count=len(visitor.constants),
        comment_count=len(actual_comments),
        non_english_count=len(all_non_english),
        function_count=len(visitor.function_names),
        class_count=len(visitor.class_names),
        variable_count=len(visitor.variables),
        docstring_count=len(visitor.docstrings)
    )

def analyze_file(file_path: str) -> ParseResult:
    """Analyze a Python file and return parsing results"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return analyze_code(content)
