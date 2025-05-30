import matplotlib.pyplot as plt
import numpy as np
from python_code_parser import analyze_code

# Test code with mixed language content
test_code = '''
# 多语言测试文件 - Multilingual Test File - マルチ言語テスト
class 基本クラス:
    """Base class for testing"""
    def __init__(self):
        self.变量 = "测试"
        self.テスト = "テスト"
        self.КОНСТАНТА = "Привет"
        
    def процесс(self):
        """Russian method"""
        return "Выполнено"
        
    def テスト関数(self):
        """Japanese method"""
        return "完了"
        
    def 处理(self):
        """Chinese method"""
        return "完成"

def main():
    # Emoji test
    status = "Success 📈"
    error = "Failed 📉"
    
    # Extended Latin
    résumé = "Café"
    
    # Mixed scripts
    data = {
        "jp": "こんにちは",
        "cn": "你好",
        "kr": "안녕하세요",
        "ru": "Привет",
        "ar": "مرحبا",
        "th": "สวัสดี"
    }
    
    # Constants
    MAX_サイズ = 100
    MIN_크기 = 0
    
    return "Done! ✅"
'''

def visualize_parser_results():
    # Analyze the code
    result = analyze_code(test_code)
    
    # Set figure size and style
    plt.rcParams['figure.figsize'] = [20, 12]
    plt.rcParams['axes.grid'] = True
    plt.rcParams['axes.axisbelow'] = True
    
    # Create figure with subplots
    fig = plt.figure()
    
    # 1. Language Distribution (Pie Chart)
    ax1 = fig.add_subplot(231)
    language_counts = {
        'Japanese': len([x for x in result.non_english if any(c in 'あいうえおアイウエオ' for c in x)]),
        'Chinese': len([x for x in result.non_english if any(c in '的是不我有' for c in x)]),
        'Korean': len([x for x in result.non_english if any(c in '한글' for c in x)]),
        'Russian': len([x for x in result.non_english if any(c in 'абвгд' for c in x)]),
        'Arabic': len([x for x in result.non_english if any(c in 'مرحبا' for c in x)]),
        'Thai': len([x for x in result.non_english if any(c in 'สวัสดี' for c in x)]),
        'Other': len([x for x in result.non_english if not any(c in 'あいうえおアイウエオ的是不我有한글абвгдمرحباสวัสดี' for c in x)])
    }
    
    # Filter out zero values
    language_counts = {k: v for k, v in language_counts.items() if v > 0}
    
    if language_counts:
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99FFCC', '#FFB366']
        wedges, texts, autotexts = ax1.pie(list(language_counts.values()), 
                                          labels=list(language_counts.keys()), 
                                          autopct='%1.1f%%', 
                                          colors=colors[:len(language_counts)])
        plt.setp(autotexts, size=8, weight="bold")
    else:
        ax1.text(0.5, 0.5, 'No non-English content found', 
                horizontalalignment='center', verticalalignment='center')
    
    ax1.set_title('Non-English Content Distribution by Language', pad=20)
    
    # 2. Code Elements Comparison (Bar Chart)
    ax2 = fig.add_subplot(232)
    categories = ['Classes', 'Functions', 'Variables', 'Constants', 'Docstrings']
    english_counts = [
        max(0, result.class_count - len(result.non_english_class_names)),
        max(0, result.function_count - len(result.non_english_function_names)),
        max(0, result.variable_count - len(result.non_english_variables)),
        max(0, result.constant_count - len(result.non_english_constants)),
        max(0, result.docstring_count - len(result.non_english_docstrings))
    ]
    non_english_counts = [
        len(result.non_english_class_names),
        len(result.non_english_function_names),
        len(result.non_english_variables),
        len(result.non_english_constants),
        len(result.non_english_docstrings)
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax2.bar(x - width/2, english_counts, width, label='English', color='#66B2FF')
    ax2.bar(x + width/2, non_english_counts, width, label='Non-English', color='#FF9999')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, rotation=45)
    ax2.set_title('Code Elements: English vs Non-English', pad=20)
    ax2.legend()
    
    # 3. Non-English Elements by Category (Horizontal Bar Chart)
    ax3 = fig.add_subplot(233)
    non_english_categories = [
        'Class Names',
        'Function Names',
        'Variables',
        'Constants',
        'Docstrings',
        'Comments',
        'Literals'
    ]
    non_english_counts = [
        len(result.non_english_class_names),
        len(result.non_english_function_names),
        len(result.non_english_variables),
        len(result.non_english_constants),
        len(result.non_english_docstrings),
        len(result.non_english_comments),
        len(result.non_english_literals)
    ]
    
    y_pos = np.arange(len(non_english_categories))
    ax3.barh(y_pos, non_english_counts, color='#FF9999')
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(non_english_categories)
    ax3.set_title('Non-English Elements by Category', pad=20)
    
    # 4. Detection Accuracy (Radar Chart)
    ax4 = fig.add_subplot(234, projection='polar')
    categories = ['Language\nDetection', 'Class\nDetection', 'Function\nDetection', 
                 'Variable\nDetection', 'Constant\nDetection', 'Docstring\nDetection']
    values = [78.3, 100, 100, 16.7, 100, 100]  # From our accuracy test
    
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
    values = np.concatenate((values, [values[0]]))  # Repeat the first value to close the polygon
    angles = np.concatenate((angles, [angles[0]]))  # Repeat the first angle to close the polygon
    
    ax4.plot(angles, values, 'o-', linewidth=2, color='#66B2FF')
    ax4.fill(angles, values, alpha=0.25, color='#66B2FF')
    ax4.set_thetagrids(angles[:-1] * 180/np.pi, categories)
    ax4.set_title('Parser Detection Accuracy (%)', pad=20)
    ax4.grid(True)
    
    # 5. Content Type Distribution (Donut Chart)
    ax5 = fig.add_subplot(235)
    content_types = {
        'Code': max(0, len(result.identifiers) - len(result.non_english)),
        'Non-English': len(result.non_english),
        'Comments': len(result.comments),
        'Docstrings': len(result.docstrings)
    }
    
    # Filter out zero values
    content_types = {k: v for k, v in content_types.items() if v > 0}
    
    if content_types:
        colors = ['#66B2FF', '#FF9999', '#99FF99', '#FFCC99']
        wedges, texts, autotexts = ax5.pie(list(content_types.values()), 
                                          labels=list(content_types.keys()),
                                          autopct='%1.1f%%',
                                          colors=colors[:len(content_types)],
                                          pctdistance=0.85,
                                          wedgeprops=dict(width=0.5))
        plt.setp(autotexts, size=8, weight="bold")
    else:
        ax5.text(0.5, 0.5, 'No content found', 
                horizontalalignment='center', verticalalignment='center')
    
    ax5.set_title('Content Type Distribution', pad=20)
    
    # Add a title to the entire figure
    fig.suptitle('Python Code Parser Analysis Results', fontsize=16, y=1.02)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the visualization
    plt.savefig('parser_analysis.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'parser_analysis.png'")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    visualize_parser_results() 