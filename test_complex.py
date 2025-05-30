from python_code_parser import analyze_file
from collections import defaultdict
import json
import regex  # For better Unicode support

def analyze_languages():
    """Analyze the complex test file and show detailed statistics"""
    result = analyze_file('complex_test.py')
    data = result.to_dict()
    
    # Track languages by category
    language_stats = defaultdict(lambda: defaultdict(int))
    
    def detect_language(text):
        """
        Enhanced language detection using Unicode ranges and script analysis.
        """
        if not text:
            return 'Unknown'
            
        # Define character ranges for different scripts
        scripts = {
            'Japanese_Hiragana': regex.compile(r'[\u3040-\u309F]'),
            'Japanese_Katakana': regex.compile(r'[\u30A0-\u30FF]'),
            'Japanese_Kanji': regex.compile(r'[\u4E00-\u9FFF][\u3040-\u309F\u30A0-\u30FF]'),
            'Chinese': regex.compile(r'[\u4E00-\u9FFF]'),
            'Korean': regex.compile(r'[\uAC00-\uD7AF\u1100-\u11FF]'),
            'Russian': regex.compile(r'[\u0400-\u04FF]'),
            'Arabic': regex.compile(r'[\u0600-\u06FF]'),
            'Thai': regex.compile(r'[\u0E00-\u0E7F]'),
            'Greek': regex.compile(r'[\u0370-\u03FF]'),
            'Hebrew': regex.compile(r'[\u0590-\u05FF]'),
            'Devanagari': regex.compile(r'[\u0900-\u097F]'),
            'Extended_Latin': regex.compile(r'[À-ÿ]')
        }
        
        # Count characters in each script
        script_counts = defaultdict(int)
        total_chars = len(text)
        
        # Check for emojis first
        emoji_pattern = regex.compile(r'[\p{Emoji_Presentation}\p{Extended_Pictographic}]')
        emoji_count = len(emoji_pattern.findall(text))
        if emoji_count == total_chars:
            return 'Emoji'
        
        # Count occurrences of each script
        for script_name, pattern in scripts.items():
            matches = pattern.findall(text)
            script_counts[script_name] = len(matches)
        
        # Special handling for Japanese vs Chinese
        if script_counts['Japanese_Hiragana'] > 0 or script_counts['Japanese_Katakana'] > 0:
            return 'Japanese'
        elif script_counts['Japanese_Kanji'] > 0:
            return 'Japanese'
        elif script_counts['Chinese'] > 0:
            return 'Chinese'
        
        # Check other scripts
        for script_name in scripts:
            if script_counts[script_name] > 0:
                return script_name.split('_')[0]  # Remove the script subtype
        
        # Handle mixed scripts
        non_latin_chars = sum(script_counts.values())
        if non_latin_chars > 0:
            # Find the dominant script
            dominant_script = max(script_counts.items(), key=lambda x: x[1])[0]
            return dominant_script.split('_')[0]
            
        return 'Other'
    
    def analyze_category(category_name, items):
        print(f"\n{category_name}:")
        if not items:
            print("  No items found")
            return
            
        for item in sorted(items):
            lang = detect_language(item)
            language_stats[category_name][lang] += 1
            print(f"  - {item} ({lang})")
    
    # Print detailed statistics
    print("=== Enhanced Code Analysis ===")
    print("\nCounts:")
    counts = data['counts']
    for key, value in counts.items():
        print(f"  {key}: {value}")
    
    # Analyze each category
    instances = data['instances']
    categories = [
        ('Identifiers', 'non_english_identifiers'),
        ('Constants', 'non_english_constants'),
        ('Class Names', 'non_english_class_names'),
        ('Function Names', 'non_english_function_names'),
        ('Variables', 'non_english_variables'),
        ('Docstrings', 'non_english_docstrings'),
        ('Comments', 'non_english_comments'),
        ('Literals', 'non_english_literals')
    ]
    
    for display_name, key in categories:
        analyze_category(display_name, instances[key])
    
    # Print language distribution
    print("\nLanguage Distribution by Category:")
    for category in language_stats:
        print(f"\n{category}:")
        total = sum(language_stats[category].values())
        for lang, count in sorted(language_stats[category].items()):
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"  {lang}: {count} ({percentage:.1f}%)")
    
    # Print emoji statistics
    emoji_count = sum(1 for items in instances.values() 
                     for item in items if detect_language(item) == 'Emoji')
    if emoji_count:
        print(f"\nEmoji Usage: Found {emoji_count} emoji(s) in the code")

if __name__ == '__main__':
    analyze_languages() 