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
        def filter_empty(s: set) -> list:
            # Keep Korean text intact
            return [x for x in s if x and (x.strip() or any(0xAC00 <= ord(c) <= 0xD7A3 or 0x1100 <= ord(c) <= 0x11FF or 0x3130 <= ord(c) <= 0x318F for c in x))]
            
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
                'keywords': filter_empty(self.keywords),
                'identifiers': filter_empty(self.identifiers),
                'literals': filter_empty(self.literals),
                'constants': filter_empty(self.constants),
                'comments': filter_empty(self.comments),
                'non_english': filter_empty(self.non_english),
                'module_attrs': filter_empty(self.module_attrs),
                'function_names': filter_empty(self.function_names),
                'class_names': filter_empty(self.class_names),
                'variables': filter_empty(self.variables),
                'docstrings': filter_empty(self.docstrings),
                'non_english_identifiers': filter_empty(self.non_english_identifiers),
                'non_english_literals': filter_empty(self.non_english_literals),
                'non_english_class_names': filter_empty(self.non_english_class_names),
                'non_english_function_names': filter_empty(self.non_english_function_names),
                'non_english_variables': filter_empty(self.non_english_variables),
                'non_english_docstrings': filter_empty(self.non_english_docstrings),
                'non_english_constants': filter_empty(self.non_english_constants),
                'non_english_comments': filter_empty(self.non_english_comments)
            }
        }

def is_english_word(text: str) -> bool:
    """
    Enhanced check to determine if a word is English or programming-related.
    """
    # Common programming/technical terms that should be considered English
    common_tech_terms = {
        'api', 'args', 'row', 'head', 'data', 'file', 'type', 'key', 'value',
        'id', 'url', 'uri', 'sql', 'xml', 'json', 'html', 'css', 'js',
        'get', 'set', 'put', 'post', 'delete', 'patch', 'options',
        'class', 'def', 'func', 'var', 'const', 'let', 'enum',
        'true', 'false', 'null', 'none', 'undefined'
    }
    
    # Clean the text
    cleaned = text.lower().strip('_-[](){}.,;:#@ \t\n')
    
    # If nothing left after cleaning, consider it English
    if not cleaned:
        return True
        
    # Check if it's a common tech term
    if cleaned in common_tech_terms:
        return True
    
    # Check if it contains only ASCII letters, numbers, and common punctuation
    return all(ord(c) < 128 and (c.isalnum() or c in '_-[](){}.,;:#@ \t\n') for c in text)

def detect_languages_in_text(text: str) -> set:
    """
    Detect all languages present in a text.
    Returns a set of language codes found.
    """
    languages = set()
    
    # Skip if text is empty, whitespace, or contains only ASCII
    if not text or text.isspace() or all(ord(c) < 128 for c in text):
        return languages
    
    # Clean the text of common programming symbols
    cleaned_text = re.sub(r'[!@#$%^&*()?":{}|<>]', ' ', text)
    cleaned_text = cleaned_text.strip()
    
    # Skip if nothing left after cleaning
    if not cleaned_text:
        return languages
    
    # First check for Korean characters (Hangul)
    if any(0xAC00 <= ord(c) <= 0xD7A3 or 0x1100 <= ord(c) <= 0x11FF or 0x3130 <= ord(c) <= 0x318F for c in cleaned_text):
        languages.add('ko')
        return languages
    
    # Split into words and check each word
    words = re.findall(r'\S+', cleaned_text)
    non_english_words = []
    
    for word in words:
        if not is_english_word(word) and any(ord(c) > 127 for c in word):
            non_english_words.append(word)
    
    # If we found non-English words, try to detect their language
    if non_english_words:
        try:
            combined_text = ' '.join(non_english_words)
            lang = detect(combined_text)
            if lang != 'en':
                languages.add(lang)
        except LangDetectException:
            # If detection fails but we have non-ASCII characters,
            # only mark as unknown if we're confident it's not English
            if any(not is_english_word(word) and any(ord(c) > 127 for c in word) 
                  for word in non_english_words):
                languages.add('unknown')
    
    return languages

def is_non_english(text: str) -> bool:
    """
    Enhanced check for non-English content.
    Now handles mixed-language content better and avoids false positives.
    """
    # Skip empty strings, whitespace, and strings with only numbers/symbols
    if not text or not text.strip() or re.match(r'^[\d\s\W_]*$', text):
        return False
    
    # Remove common programming symbols and clean up
    text = text.strip('# ')
    text = re.sub(r'[!@#$%^&*()?":{}|<>]', ' ', text)
    
    # Skip if cleaned text is empty
    if not text.strip():
        return False
    
    # First check for Korean characters (Hangul)
    if any(0xAC00 <= ord(c) <= 0xD7A3 or 0x1100 <= ord(c) <= 0x11FF or 0x3130 <= ord(c) <= 0x318F for c in text):
        return True
    
    # Split into words
    words = text.split()
    
    # If all words are English or common programming terms, it's not non-English
    if all(is_english_word(word) for word in words):
        return False
    
    # Check for non-ASCII characters and non-English words
    for word in words:
        # Skip if word is a common programming term
        if word.lower() in {'api', 'url', 'json', 'xml', 'html', 'css', 'js', 'http', 'https', 'ftp', 'ssh', 'tcp', 'udp', 'ip', 'dns', 'sql', 'db', 'gui', 'ui', 'ux', 'cli', 'sdk', 'api', 'rest', 'soap', 'jwt', 'oauth', 'saml', 'ldap', 'ssl', 'tls', 'csv', 'pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'tar', 'gz', 'rar', '7z', 'exe', 'dll', 'lib', 'jar', 'war', 'ear', 'apk', 'ipa', 'deb', 'rpm', 'msi', 'iso', 'img', 'dmg', 'pkg', 'app', 'bin', 'sh', 'bat', 'cmd', 'ps1', 'vbs', 'js', 'py', 'rb', 'php', 'java', 'cpp', 'cs', 'go', 'rs', 'ts', 'jsx', 'tsx', 'vue', 'html', 'css', 'scss', 'sass', 'less', 'md', 'rst', 'tex', 'yaml', 'yml', 'toml', 'ini', 'conf', 'cfg', 'env', 'log', 'tmp', 'temp', 'cache', 'bak', 'old', 'new', 'test', 'tests', 'spec', 'specs', 'mock', 'mocks', 'stub', 'stubs', 'fake', 'fakes', 'fixture', 'fixtures', 'helper', 'helpers', 'util', 'utils', 'lib', 'libs', 'vendor', 'node_modules', 'packages', 'dist', 'build', 'release', 'debug', 'prod', 'dev', 'staging', 'qa', 'test', 'local', 'remote', 'master', 'main', 'develop', 'dev', 'feature', 'bugfix', 'hotfix', 'release', 'support', 'patch', 'fix', 'feat', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert'}:
            continue
            
        # Check for non-ASCII characters
        if any(ord(c) > 127 for c in word):
            return True
            
        # Check if word is not English
        if not is_english_word(word):
            return True
            
    return False

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
        # Only add non-empty strings to literals
        if value and value.strip():
            self.literals.add(value)
            if is_non_english(value):
                # For strings, split and store non-English parts
                for word in re.findall(r'[^\s!@#$%^&*(),.?":{}|<>]+', value):
                    if word.strip() and any(ord(c) > 127 for c in word):
                        self.non_english.add(word)
                        self.non_english_literals.add(word)
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Handle constants (Python 3.8+)"""
        if isinstance(node.value, str):
            value = node.value
            # Only add non-empty strings to literals
            if value and value.strip():
                self.literals.add(value)
                if is_non_english(value):
                    # For strings, split and store non-English parts
                    for word in re.findall(r'[^\s!@#$%^&*(),.?":{}|<>]+', value):
                        if word.strip() and any(ord(c) > 127 for c in word):
                            self.non_english.add(word)
                            self.non_english_literals.add(word)
        elif isinstance(node.value, (int, float, bool, type(None))):
            const_str = str(node.value)
            if const_str.strip():
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
        # First check for Korean characters (Hangul)
        has_korean = any(0xAC00 <= ord(c) <= 0xD7A3 or 0x1100 <= ord(c) <= 0x11FF or 0x3130 <= ord(c) <= 0x318F for c in content)
        
        if is_docstring:
            docstrings.add(content)
            if has_korean or is_non_english(content):
                non_english_docstrings.add(content)
                non_english_comments.add(content)  # Also add to non-English comments
        else:
            # For comments, preserve the entire comment if it contains Korean characters
            comments.add(content)
            if has_korean or is_non_english(content):
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
    
    # Filter out empty strings from all collections
    def filter_empty(s: set) -> set:
        # Keep Korean text intact
        return {x for x in s if x and (x.strip() or any(0xAC00 <= ord(c) <= 0xD7A3 or 0x1100 <= ord(c) <= 0x11FF or 0x3130 <= ord(c) <= 0x318F for c in x))}
    
    # Clean all sets in the visitor
    visitor.literals = filter_empty(visitor.literals)
    visitor.constants = filter_empty(visitor.constants)
    visitor.comments = filter_empty(visitor.comments)
    visitor.non_english = filter_empty(visitor.non_english)
    visitor.module_attrs = filter_empty(visitor.module_attrs)
    visitor.function_names = filter_empty(visitor.function_names)
    visitor.class_names = filter_empty(visitor.class_names)
    visitor.variables = filter_empty(visitor.variables)
    visitor.docstrings = filter_empty(visitor.docstrings)
    visitor.non_english_identifiers = filter_empty(visitor.non_english_identifiers)
    visitor.non_english_literals = filter_empty(visitor.non_english_literals)
    visitor.non_english_class_names = filter_empty(visitor.non_english_class_names)
    visitor.non_english_function_names = filter_empty(visitor.non_english_function_names)
    visitor.non_english_variables = filter_empty(visitor.non_english_variables)
    visitor.non_english_docstrings = filter_empty(visitor.non_english_docstrings)
    visitor.non_english_constants = filter_empty(visitor.non_english_constants)
    visitor.non_english_comments = filter_empty(visitor.non_english_comments)
    visitor.identifiers = filter_empty(visitor.identifiers)
    
    return ParseResult(
        keywords=visitor.keywords,
        identifiers=visitor.identifiers,
        literals=visitor.literals,
        constants=visitor.constants,
        comments=visitor.comments,
        non_english=visitor.non_english,
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
        comment_count=len(visitor.comments),
        non_english_count=len(visitor.non_english),
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
