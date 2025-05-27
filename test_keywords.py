from python_code_parser import analyze_code
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Test code with various Python keywords
test_code = '''
def test_function():
    try:
        if True:
            for i in range(10):
                while i > 0:
                    if i == 5:
                        break
                    elif i == 3:
                        continue
                    else:
                        i -= 1
    except Exception as e:
        pass
    finally:
        return None

class TestClass:
    def __init__(self):
        self.value = None
        
    async def async_method(self):
        await something()
        
    @property
    def prop(self):
        return self.value
        
    def with_test(self):
        with open('file.txt') as f:
            pass
            
    def import_test(self):
        from os import path as os_path
        import sys
        global x
        nonlocal y
        assert True
        yield 1
        del x
        raise Exception
'''

# Analyze the code
result = analyze_code(test_code)

print("\nFound Keywords:")
print(sorted(list(result.keywords)))
print(f"\nTotal keywords found: {result.keyword_count}") 