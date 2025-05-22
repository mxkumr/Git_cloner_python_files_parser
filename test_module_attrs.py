import unittest
from python_code_parser import analyze_code

class TestModuleAttributes(unittest.TestCase):
    def test_module_attributes(self):
        code = '''
import os
import json
from datetime import datetime

# Custom identifiers
my_variable = 123
def my_function():
    # Using module attributes
    env_var = os.environ.get('PATH')
    data = json.dumps({'key': 'value'})
    current_time = datetime.now()
    return env_var
'''
        result = analyze_code(code)
        
        print("\nIdentifiers found:", sorted(list(result.identifiers)))
        print("Module attributes:", sorted(list(result.module_attrs)))
        
        # These should be in identifiers
        self.assertIn('my_variable', result.identifiers)
        self.assertIn('my_function', result.identifiers)
        self.assertIn('env_var', result.identifiers)
        self.assertIn('data', result.identifiers)
        self.assertIn('current_time', result.identifiers)
        
        # These should NOT be in identifiers
        self.assertNotIn('os', result.identifiers)
        self.assertNotIn('environ', result.identifiers)
        self.assertNotIn('get', result.identifiers)
        self.assertNotIn('json', result.identifiers)
        self.assertNotIn('dumps', result.identifiers)
        self.assertNotIn('datetime', result.identifiers)
        self.assertNotIn('now', result.identifiers)

if __name__ == '__main__':
    unittest.main() 