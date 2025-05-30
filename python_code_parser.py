from typing import NamedTuple, Set
import ast
import unicodedata
from langdetect import detect, LangDetectException
import logging
import re
import keyword

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
    # New fields for non-English categories
    non_english_identifiers: Set[str]
    non_english_literals: Set[str]
    non_english_class_names: Set[str]
    non_english_function_names: Set[str]
    non_english_variables: Set[str]
    non_english_docstrings: Set[str]
    non_english_constants: Set[str]
    non_english_comments: Set[str]
    keyword_count: int
    identifier_count: int
    literal_count: int
    constant_count: int
    comment_count: int
    non_english_count: int
    function_count: int
    class_count: int
    variable_count: int
    docstring_count: int
    # New count fields for non-English categories
    non_english_identifier_count: int
    non_english_literal_count: int
    non_english_class_count: int
    non_english_function_count: int
    non_english_variable_count: int
    non_english_docstring_count: int
    non_english_constant_count: int
    non_english_comment_count: int

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
                'docstring_count': self.docstring_count,
                'non_english_identifier_count': self.non_english_identifier_count,
                'non_english_literal_count': self.non_english_literal_count,
                'non_english_class_count': self.non_english_class_count,
                'non_english_function_count': self.non_english_function_count,
                'non_english_variable_count': self.non_english_variable_count,
                'non_english_docstring_count': self.non_english_docstring_count,
                'non_english_constant_count': self.non_english_constant_count,
                'non_english_comment_count': self.non_english_comment_count
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
                'docstrings': list(self.docstrings),
                'non_english_identifiers': list(self.non_english_identifiers),
                'non_english_literals': list(self.non_english_literals),
                'non_english_class_names': list(self.non_english_class_names),
                'non_english_function_names': list(self.non_english_function_names),
                'non_english_variables': list(self.non_english_variables),
                'non_english_docstrings': list(self.non_english_docstrings),
                'non_english_constants': list(self.non_english_constants),
                'non_english_comments': list(self.non_english_comments)
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

def detect_languages_in_text(text: str) -> set:
    """
    Detect all languages present in a text.
    Returns a set of language codes found.
    """
    languages = set()
    
    # Skip if text is too short or only contains ASCII
    if not text or len(text.strip()) < 3 or all(ord(c) < 128 for c in text):
        return languages
    
    # Split text into words, handling mixed scripts
    words = []
    current_word = ''
    current_script = None
    
    for char in text:
        if char.isspace():
            if current_word:
                words.append(current_word)
                current_word = ''
                current_script = None
        else:
            char_script = 'ascii' if ord(char) < 128 else 'other'
            if current_script and char_script != current_script:
                if current_word:
                    words.append(current_word)
                current_word = ''
            current_word += char
            current_script = char_script
    
    if current_word:
        words.append(current_word)
    
    # Analyze each word
    for word in words:
        if any(ord(c) > 127 for c in word):
            try:
                lang = detect(word)
                if lang != 'en':
                    languages.add(lang)
            except LangDetectException:
                continue
    
    return languages

def is_non_english(text: str) -> bool:
    """
    Enhanced check for non-English content.
    Now handles mixed-language content better.
    """
    # Skip empty strings and strings with only numbers/symbols
    if not text or re.match(r'^[\d\s\W_]*$', text):
        return False
        
    # Remove common programming symbols and clean up
    text = text.strip('# ')
    text = re.sub(r'[!@#$%^&*()?":{}|<>]', '', text)
    
    # Skip common programming terms
    if text.lower() in {'str', 'int', 'dict', 'list', 'set', 'bool', 'none', 'true', 'false'}:
        return False
    
    # Check for non-ASCII characters
    has_non_ascii = any(ord(c) > 127 for c in text)
    if not has_non_ascii:
        return False
    
    # Detect languages
    languages = detect_languages_in_text(text)
    return len(languages) > 0

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
        # New sets for non-English categories
        self.non_english_identifiers = set()
        self.non_english_literals = set()
        self.non_english_class_names = set()
        self.non_english_function_names = set()
        self.non_english_variables = set()
        self.non_english_docstrings = set()
        self.non_english_constants = set()
        self.non_english_comments = set()
        # Track scope for better constant detection
        self.current_scope = []
        self.in_class_def = False

    def is_constant(self, name: str) -> bool:
        """
        Determine if a name represents a constant.
        Python convention: constants are usually UPPER_CASE.
        """
        # Built-in constants
        if name in {'True', 'False', 'None', 'NotImplemented', 'Ellipsis'}:
            return True
        
        # Check if name is in all uppercase (allowing underscores and numbers)
        if name.isupper() or (name.replace('_', '').isalnum() and 
                             any(c.isupper() for c in name) and 
                             not any(c.islower() for c in name)):
            # Make sure it's not in a class definition (where UPPER_CASE might be used for other purposes)
            if not self.in_class_def:
                return True
        
        return False

    def visit(self, node):
        """Override visit to collect keywords"""
        node_type = type(node).__name__
        
        # Map AST node types to Python keywords
        keyword_map = {
            'FunctionDef': 'def',
            'ClassDef': 'class',
            'Return': 'return',
            'Delete': 'del',
            'For': 'for',
            'While': 'while',
            'If': 'if',
            'With': 'with',
            'Raise': 'raise',
            'Try': 'try',
            'Assert': 'assert',
            'Import': 'import',
            'ImportFrom': 'from',
            'Global': 'global',
            'Nonlocal': 'nonlocal',
            'Pass': 'pass',
            'Break': 'break',
            'Continue': 'continue',
            'Lambda': 'lambda',
            'Yield': 'yield',
            'YieldFrom': 'yield from',
            'In': 'in',
            'Is': 'is',
            'And': 'and',
            'Or': 'or',
            'Not': 'not',
            'True': 'True',
            'False': 'False',
            'None': 'None'
        }
        
        if node_type in keyword_map:
            kw = keyword_map[node_type]
            self.keywords.add(kw)
            logger.debug(f"Found keyword: {kw}")
            
        # Check for async/await keywords
        if hasattr(node, 'is_async') and node.is_async:
            self.keywords.add('async')
            if isinstance(node, ast.FunctionDef):
                self.keywords.add('await')
                
        # Check for 'as' keyword in imports and with statements
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.asname:
                    self.keywords.add('as')
                    break
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars:
                    self.keywords.add('as')
                    break
                    
        # Check for 'elif' and 'else' keywords
        if isinstance(node, ast.If):
            if node.orelse:
                if any(isinstance(n, ast.If) for n in node.orelse):
                    self.keywords.add('elif')
                else:
                    self.keywords.add('else')
        
        # Continue with normal visit
        super().visit(node)

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
        """Handle variable and function names with improved constant detection"""
        name = node.id
        
        # Skip if it's a module or module attribute
        if name not in self.imported_modules and not any(name in attr for attr in self.module_attrs):
            # First, check if it's a constant
            if self.is_constant(name):
                self.constants.add(name)
                if is_non_english(name):
                    self.non_english.add(name)
                    self.non_english_constants.add(name)
            # Then handle as variable if it's being assigned
            elif isinstance(node.ctx, (ast.Store, ast.AugStore)):
                self.variables.add(name)
                if is_non_english(name):
                    self.non_english.add(name)
                    self.non_english_variables.add(name)
            
            self.identifiers.add(name)
            if is_non_english(name):
                self.non_english.add(name)
                self.non_english_identifiers.add(name)
        
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
                    self.non_english_literals.add(word)
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
                        self.non_english_literals.add(word)
        elif isinstance(node.value, (int, float, bool, type(None))):
            const_str = str(node.value)
            self.constants.add(const_str)
            if is_non_english(const_str):
                self.non_english.add(const_str)
                self.non_english_constants.add(const_str)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Handle function definitions"""
        name = node.name
        self.function_names.add(name)
        self.identifiers.add(name)
        
        # Check for docstring
        docstring = ast.get_docstring(node)
        if docstring:
            self.docstrings.add(docstring)
            if is_non_english(docstring):
                self.non_english.add(docstring)
                self.non_english_docstrings.add(docstring)
            
        if is_non_english(name):
            self.non_english.add(name)
            self.non_english_function_names.add(name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Handle async function definitions"""
        # Use the same logic as regular functions
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        """Handle class definitions with scope tracking"""
        self.current_scope.append('class')
        self.in_class_def = True
        
        name = node.name
        self.class_names.add(name)
        self.identifiers.add(name)
        
        # Check for docstring
        docstring = ast.get_docstring(node)
        if docstring:
            self.docstrings.add(docstring)
            if is_non_english(docstring):
                self.non_english.add(docstring)
                self.non_english_docstrings.add(docstring)
            
        if is_non_english(name):
            self.non_english.add(name)
            self.non_english_class_names.add(name)
            
        self.generic_visit(node)
        self.current_scope.pop()
        self.in_class_def = False

    def visit_Module(self, node):
        """Handle module-level docstrings"""
        docstring = ast.get_docstring(node)
        if docstring:
            self.docstrings.add(docstring)
            if is_non_english(docstring):
                self.non_english.add(docstring)
                self.non_english_docstrings.add(docstring)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Handle assignments with improved constant detection"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                # Check if this is a constant assignment
                if self.is_constant(name):
                    self.constants.add(name)
                    if is_non_english(name):
                        self.non_english.add(name)
                        self.non_english_constants.add(name)
                else:
                    self.variables.add(name)
                    if is_non_english(name):
                        self.non_english.add(name)
                        self.non_english_variables.add(name)
            elif isinstance(target, ast.Attribute):
                attr_name = target.attr
                if is_non_english(attr_name):
                    self.non_english.add(attr_name)
                    if self.is_constant(attr_name):
                        self.non_english_constants.add(attr_name)
                    else:
                        self.non_english_variables.add(attr_name)
                
        self.generic_visit(node)

def extract_comments(source_lines):
    """
    Enhanced comment extraction with better handling of docstrings vs comments.
    """
    comments = set()
    non_english_comments = set()
    docstrings = set()
    non_english_docstrings = set()
    
    in_multiline = False
    multiline_content = []
    last_token_type = None  # Track if we're in a docstring or comment
    
    def process_content(content, is_docstring=False):
        if is_docstring:
            docstrings.add(content)
            if is_non_english(content):
                non_english_docstrings.add(content)
        else:
            comments.add(content)
            if is_non_english(content):
                non_english_comments.add(content)
    
    for i, line in enumerate(source_lines):
        line = line.strip()
        
        # Handle multiline strings/comments
        if line.startswith('"""') or line.startswith("'''"):
            if not in_multiline:
                in_multiline = True
                multiline_content = [line.strip('"\'')]
                # Determine if this is a docstring
                last_token_type = 'docstring' if i == 0 or source_lines[i-1].strip().endswith(':') else 'comment'
            else:
                in_multiline = False
                multiline_content.append(line.strip('"\''))
                content = '\n'.join(multiline_content)
                process_content(content, is_docstring=(last_token_type == 'docstring'))
                multiline_content = []
                last_token_type = None
        elif in_multiline:
            multiline_content.append(line)
        else:
            # Handle single-line comments
            hash_pos = line.find('#')
            if hash_pos != -1:
                comment = line[hash_pos:].strip()
                if comment:  # Only add non-empty comments
                    process_content(comment, is_docstring=False)
    
    return comments, non_english_comments, docstrings, non_english_docstrings

def analyze_code(code: str) -> ParseResult:
    """
    Analyze Python code with improved handling of mixed content and docstrings.
    """
    # Parse the AST
    tree = ast.parse(code)
    visitor = PythonAstVisitor()
    visitor.visit(tree)
    
    # Extract comments and docstrings
    source_lines = code.splitlines()
    comments, non_eng_comments, docs, non_eng_docs = extract_comments(source_lines)
    
    # Update visitor's sets
    visitor.comments.update(comments)
    visitor.non_english_comments.update(non_eng_comments)
    visitor.docstrings.update(docs)
    visitor.non_english_docstrings.update(non_eng_docs)
    
    # Combine all non-English content
    all_non_english = (visitor.non_english_identifiers | 
                      visitor.non_english_literals |
                      visitor.non_english_class_names |
                      visitor.non_english_function_names |
                      visitor.non_english_variables |
                      visitor.non_english_docstrings |
                      visitor.non_english_constants |
                      visitor.non_english_comments)
    
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
        non_english_identifiers=visitor.non_english_identifiers,
        non_english_literals=visitor.non_english_literals,
        non_english_class_names=visitor.non_english_class_names,
        non_english_function_names=visitor.non_english_function_names,
        non_english_variables=visitor.non_english_variables,
        non_english_docstrings=visitor.non_english_docstrings,
        non_english_constants=visitor.non_english_constants,
        non_english_comments=visitor.non_english_comments,
        keyword_count=len(visitor.keywords),
        identifier_count=len(visitor.identifiers),
        literal_count=len(visitor.literals),
        constant_count=len(visitor.constants),
        comment_count=len(actual_comments),
        non_english_count=len(all_non_english),
        function_count=len(visitor.function_names),
        class_count=len(visitor.class_names),
        variable_count=len(visitor.variables),
        docstring_count=len(visitor.docstrings),
        non_english_identifier_count=len(visitor.non_english_identifiers),
        non_english_literal_count=len(visitor.non_english_literals),
        non_english_class_count=len(visitor.non_english_class_names),
        non_english_function_count=len(visitor.non_english_function_names),
        non_english_variable_count=len(visitor.non_english_variables),
        non_english_docstring_count=len(visitor.non_english_docstrings),
        non_english_constant_count=len(visitor.non_english_constants),
        non_english_comment_count=len(visitor.non_english_comments)
    )

def analyze_file(file_path: str) -> ParseResult:
    """Analyze a Python file and return parsing results"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return analyze_code(content)
