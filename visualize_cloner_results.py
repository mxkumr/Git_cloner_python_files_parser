import matplotlib.pyplot as plt
import json
import numpy as np
from collections import defaultdict

def load_analysis_results(file_path='analysis_output.json'):
    """Load the analysis results from the JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def aggregate_results(data):
    """Aggregate results from all files across all repositories"""
    totals = defaultdict(int)
    
    # Get summary data
    summary = data['summary']
    totals['total_repos'] = summary['total_repositories']
    totals['total_files'] = summary['total_python_files']
    totals['files_with_non_english'] = summary['total_files_with_non_english']
    
    # Aggregate counts from all files
    for repo_data in data['analysis_results']:
        for file_data in repo_data['files']:
            counts = file_data['analysis']['counts']
            for key, value in counts.items():
                totals[key] += value
    
    return dict(totals)

def create_bar_charts(data):
    """Create separate bar charts for English and non-English content"""
    # Set style parameters
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = [15, 10]
    plt.rcParams['axes.grid'] = True
    plt.rcParams['axes.axisbelow'] = True
    
    # Create a figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2)
    
    # Prepare data for English content
    english_data = {
        'Total Files': data['total_files'],
        'Files with\nNon-English': data['files_with_non_english'],
        'Identifiers': data['identifier_count'] - data['non_english_identifier_count'],
        'Comments': data['comment_count'] - data['non_english_comment_count'],
        'Docstrings': data['docstring_count'] - data['non_english_docstring_count'],
        'Functions': data['function_count'] - data['non_english_function_count'],
        'Classes': data['class_count'] - data['non_english_class_count'],
        'Variables': data['variable_count'] - data['non_english_variable_count'],
        'Constants': data['constant_count'] - data['non_english_constant_count']
    }
    
    # Prepare data for non-English content
    non_english_data = {
        'Identifiers': data['non_english_identifier_count'],
        'Comments': data['non_english_comment_count'],
        'Docstrings': data['non_english_docstring_count'],
        'Functions': data['non_english_function_count'],
        'Classes': data['non_english_class_count'],
        'Variables': data['non_english_variable_count'],
        'Constants': data['non_english_constant_count'],
        'Literals': data['non_english_literal_count']
    }
    
    # Plot English content
    x1 = np.arange(len(english_data))
    bars1 = ax1.bar(x1, list(english_data.values()), color='#66B2FF')
    ax1.set_xticks(x1)
    ax1.set_xticklabels(english_data.keys(), rotation=45, ha='right')
    ax1.set_title('English Content Distribution')
    ax1.set_ylabel('Count')
    
    # Add value labels on top of bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom')
    
    # Plot non-English content
    x2 = np.arange(len(non_english_data))
    bars2 = ax2.bar(x2, list(non_english_data.values()), color='#FF9999')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(non_english_data.keys(), rotation=45, ha='right')
    ax2.set_title('Non-English Content Distribution')
    ax2.set_ylabel('Count')
    
    # Add value labels on top of bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom')
    
    # Add repository information
    repo_info = (
        f"Repository Analysis Summary\n"
        f"Total Repositories: {data['total_repos']:,}\n"
        f"Total Python Files: {data['total_files']:,}\n"
        f"Files with Non-English Content: {data['files_with_non_english']:,}"
    )
    plt.figtext(0.5, 0.95, repo_info, ha='center', va='top', fontsize=12)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)  # Make room for the title
    
    # Save the visualization
    plt.savefig('cloner_analysis.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'cloner_analysis.png'")
    
    # Show the plot
    plt.show()

def main():
    try:
        # Load and aggregate the analysis results
        raw_data = load_analysis_results()
        aggregated_data = aggregate_results(raw_data)
        
        # Create the visualizations
        create_bar_charts(aggregated_data)
        
    except FileNotFoundError:
        print("Error: analysis_output.json file not found. Please make sure the file exists in the current directory.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in analysis_output.json file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 