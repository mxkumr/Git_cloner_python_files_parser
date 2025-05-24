from typing import List, Dict, NamedTuple, Set
import re
from tree_sitter import Language, Parser
import os
from pathlib import Path
import unicodedata
from langdetect import detect, LangDetectException
import logging

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

def is_non_english(text: str) -> bool:
    """
    Check if text contains non-English characters using Unicode properties.
    Returns True if text contains characters outside basic Latin alphabet.
    """
    # Skip empty strings and common symbols
    if not text or text.isspace() or text.isdigit():
        return False
        
    # Common programming symbols and characters to ignore
    common_symbols = set('_-+=/<>[](){}.,;:!@#$%^&*\\|`~"\'')
    
    for char in text:
        if char in common_symbols or char.isspace():
            continue
            
        # Get Unicode category and script
        category = unicodedata.category(char)
        try:
            script = unicodedata.name(char).split()[0]
        except ValueError:
            continue
            
        # Check if character is outside basic Latin alphabet
        if (not category.startswith('L') or  # Not a letter
            (category.startswith('L') and script not in ['LATIN', 'BASIC'])):
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

class PythonCodeParser:
    def __init__(self):
        # Initialize tree-sitter parser
        self.parser = Parser()
        
        # Build and load the Python grammar
        py_language_path = os.path.join(os.path.dirname(__file__), 'build', 'my-languages.so')
        if not os.path.exists(py_language_path):
            self._build_language()
            
        PY_LANGUAGE = Language(py_language_path, 'python')
        self.parser.set_language(PY_LANGUAGE)

    def _build_language(self):
        """Build the tree-sitter Python grammar"""
        from tree_sitter import Language
        
        # Create build directory if it doesn't exist
        build_dir = os.path.join(os.path.dirname(__file__), 'build')
        os.makedirs(build_dir, exist_ok=True)
        
        # Clone the Python grammar repository if needed
        grammar_path = os.path.join(build_dir, 'tree-sitter-python')
        if not os.path.exists(grammar_path):
            os.system(f'git clone https://github.com/tree-sitter/tree-sitter-python {grammar_path}')
            
        # Build the language
        Language.build_library(
            os.path.join(build_dir, 'my-languages.so'),
            [grammar_path]
        )

    def _extract_text(self, node, source_bytes: bytes) -> str:
        """Extract text from a node"""
        return source_bytes[node.start_byte:node.end_byte].decode('utf-8')

    def _process_node(self, node, source_bytes: bytes, results: Dict[str, Set[str]]):
        """Process a single node and extract relevant information"""
        if node.type == 'comment':
            text = self._extract_text(node, source_bytes)
            results['comments'].add(text)
            if is_non_english(text):
                results['non_english'].add(text)
                
        elif node.type == 'string':
            text = self._extract_text(node, source_bytes)
            results['literals'].add(text)
            if is_non_english(text):
                results['non_english'].add(text)
                
        elif node.type == 'identifier':
            text = self._extract_text(node, source_bytes)
            results['identifiers'].add(text)
            if is_non_english(text):
                results['non_english'].add(text)
                
        elif node.type in ['true', 'false', 'none', 'number']:
            text = self._extract_text(node, source_bytes)
            results['constants'].add(text)
            
        elif node.type == 'keyword':
            text = self._extract_text(node, source_bytes)
            results['keywords'].add(text)

        # Recursively process child nodes
        for child in node.children:
            self._process_node(child, source_bytes, results)

    def analyze_code(self, code: str) -> ParseResult:
        """
        Analyze Python code and extract various components including non-English content.
        
        Args:
            code: Python source code as string
            
        Returns:
            ParseResult containing sets of different code components and their counts
        """
        # Convert code to bytes for tree-sitter
        source_bytes = bytes(code, 'utf8')
        
        # Parse the code
        tree = self.parser.parse(source_bytes)
        
        # Initialize results
        results = {
            'keywords': set(),
            'identifiers': set(),
            'literals': set(),
            'constants': set(),
            'comments': set(),
            'non_english': set()
        }
        
        # Process the syntax tree
        self._process_node(tree.root_node, source_bytes, results)
        
        # Create and return ParseResult
        return ParseResult(
            keywords=results['keywords'],
            identifiers=results['identifiers'],
            literals=results['literals'],
            constants=results['constants'],
            comments=results['comments'],
            non_english=results['non_english'],
            keyword_count=len(results['keywords']),
            identifier_count=len(results['identifiers']),
            literal_count=len(results['literals']),
            constant_count=len(results['constants']),
            comment_count=len(results['comments']),
            non_english_count=len(results['non_english'])
        )

def analyze_file(file_path: str) -> ParseResult:
    """Analyze a Python file and return parsing results"""
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    parser = PythonCodeParser()
    return parser.analyze_code(code)
