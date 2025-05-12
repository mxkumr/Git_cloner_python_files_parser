import libcst as cst
from langdetect import detect
import keyword

class AnalysisResult:
    def __init__(self, keywords, identifiers, literals, constants, comments, non_english):
        self.keywords = set(keywords)
        self.identifiers = set(identifiers)
        self.literals = list(literals)
        self.constants = list(constants)
        self.comments = list(comments)
        self.non_english = list(non_english)

        # Counts
        self.keyword_count = len(self.keywords)
        self.identifier_count = len(self.identifiers)
        self.literal_count = len(self.literals)
        self.constant_count = len(self.constants)
        self.comment_count = len(self.comments)
        self.non_english_count = len(self.non_english)

class CodeAnalyzer(cst.CSTVisitor):
    def __init__(self):
        self.keywords = set()
        self.identifiers = set()
        self.literals = []
        self.constants = []
        self.comments = []
        self.non_english = []

    def visit_Name(self, node: cst.Name):
        if keyword.iskeyword(node.value):
            self.keywords.add(node.value)
        else:
            self.identifiers.add(node.value)

    def visit_SimpleString(self, node: cst.SimpleString):
        value = node.value.strip("\"'")
        self.literals.append(value)
        try:
            lang = detect(value)
            if lang != "en":
                self.non_english.append(value)
        except:
            pass

    def visit_Integer(self, node: cst.Integer):
        self.constants.append(node.value)

    def visit_Float(self, node: cst.Float):
        self.constants.append(node.value)

    def visit_Comment(self, node: cst.Comment):
        comment_text = node.value.strip("#").strip()
        self.comments.append(comment_text)
        try:
            lang = detect(comment_text)
            if lang != "en":
                self.non_english.append(comment_text)
        except:
            pass

def analyze_code(code):
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    analyzer = CodeAnalyzer()
    wrapper.visit(analyzer)
    return AnalysisResult(
        analyzer.keywords,
        analyzer.identifiers,
        analyzer.literals,
        analyzer.constants,
        analyzer.comments,
        analyzer.non_english
    )
