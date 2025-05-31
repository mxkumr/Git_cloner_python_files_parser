import matplotlib.pyplot as plt
import json
import numpy as np
from collections import defaultdict
import os

def load_analysis_results(file_path='analysis_output.json'):
    """Load the analysis results from the JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_repo_visualizations(data, output_folder):
    """Create combined visualizations (bar graphs and pie chart) for each repository"""
    # Set style parameters
    plt.style.use('default')
    
    # Process each repository
    for repo_idx, repo_data in enumerate(data['analysis_results']):
        repo_name = repo_data['repository']
        
        # Aggregate data for this repository
        english_data = defaultdict(int)
        non_english_data = defaultdict(int)
        
        for file_data in repo_data['files']:
            counts = file_data['analysis']['counts']
            
            # English content
            english_data['Identifiers'] += counts['identifier_count'] - counts['non_english_identifier_count']
            english_data['Comments'] += counts['comment_count'] - counts['non_english_comment_count']
            english_data['Docstrings'] += counts['docstring_count'] - counts['non_english_docstring_count']
            english_data['Functions'] += counts['function_count'] - counts['non_english_function_count']
            english_data['Classes'] += counts['class_count'] - counts['non_english_class_count']
            english_data['Variables'] += counts['variable_count'] - counts['non_english_variable_count']
            english_data['Constants'] += counts['constant_count'] - counts['non_english_constant_count']
            
            # Non-English content
            non_english_data['Identifiers'] += counts['non_english_identifier_count']
            non_english_data['Comments'] += counts['non_english_comment_count']
            non_english_data['Docstrings'] += counts['non_english_docstring_count']
            non_english_data['Functions'] += counts['non_english_function_count']
            non_english_data['Classes'] += counts['non_english_class_count']
            non_english_data['Variables'] += counts['non_english_variable_count']
            non_english_data['Constants'] += counts['non_english_constant_count']
            non_english_data['Literals'] += counts['non_english_literal_count']
        
        # Create figure with three subplots (2 for bars, 1 for pie)
        fig = plt.figure(figsize=(20, 10))  # Increased height from 8 to 10
        
        # Add repository name as a separate title with padding
        fig.suptitle(f'Repository: {repo_name}', fontsize=16, y=0.98)  # Moved title up
        
        # Create subplot grid with more space at top
        gs = fig.add_gridspec(1, 3, top=0.85)  # Reduced top margin to create more space
        
        # Plot English content (bar)
        ax1 = fig.add_subplot(gs[0, 0])
        categories = list(english_data.keys())
        values = list(english_data.values())
        x = np.arange(len(categories))
        bars1 = ax1.bar(x, values, color='#66B2FF')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, rotation=45, ha='right')
        ax1.set_title('English Content', pad=20)  # Added padding to subplot title
        ax1.set_ylabel('Count')
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom')
        
        # Plot Non-English content (bar)
        ax2 = fig.add_subplot(gs[0, 1])
        categories = list(non_english_data.keys())
        values = list(non_english_data.values())
        x = np.arange(len(categories))
        bars2 = ax2.bar(x, values, color='#FF9999')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, rotation=45, ha='right')
        ax2.set_title('Non-English Content', pad=20)  # Added padding to subplot title
        ax2.set_ylabel('Count')
        
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom')
        
        # Create pie chart
        ax3 = fig.add_subplot(gs[0, 2])
        total_english = sum(english_data.values())
        total_non_english = sum(non_english_data.values())
        total = total_english + total_non_english
        
        if total == 0:
            # If there's no data, show a message
            ax3.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
            ax3.set_title('Content Distribution\n(No Data)', pad=20)  # Added padding to subplot title
        else:
            # Main pie chart (English vs Non-English)
            main_sizes = [total_english, total_non_english]
            main_labels = [
                f'English\n({total_english/total*100:.1f}%)',
                f'Non-English\n({total_non_english/total*100:.1f}%)'
            ]
            colors = ['#66B2FF', '#FF9999']
            
            ax3.pie(main_sizes, labels=main_labels, colors=colors, autopct='%1.1f%%',
                   startangle=90, pctdistance=0.85)
            
            # Create a smaller circle at the center
            centre_circle = plt.Circle((0,0), 0.70, fc='white')
            ax3.add_artist(centre_circle)
            
            # Add category breakdown in the center
            if total_non_english > 0:
                category_text = "Non-English Breakdown:\n"
                for category, value in non_english_data.items():
                    if value > 0:
                        percentage = (value / total_non_english) * 100
                        category_text += f"{category}: {percentage:.1f}%\n"
                ax3.text(0, 0, category_text, ha='center', va='center', fontsize=8)
            
            ax3.set_title('Content Distribution', pad=20)  # Added padding to subplot title
        
        # Adjust layout with more space between plots and labels
        plt.tight_layout(rect=[0, 0, 1, 0.90])  # Adjusted rect parameter to prevent overlap
        output_path = os.path.join(output_folder, f'repo_analysis_{repo_idx + 1}.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

def create_overall_pie_chart(data, output_folder):
    """Create a pie chart showing overall distribution of English vs Non-English content"""
    total_english = 0
    total_non_english = 0
    categories = defaultdict(int)
    
    # Aggregate data across all repositories
    for repo_data in data['analysis_results']:
        english_data = defaultdict(int)
        non_english_data = defaultdict(int)
        
        for file_data in repo_data['files']:
            counts = file_data['analysis']['counts']
            
            # English content
            english_data['Identifiers'] += counts['identifier_count'] - counts['non_english_identifier_count']
            english_data['Comments'] += counts['comment_count'] - counts['non_english_comment_count']
            english_data['Docstrings'] += counts['docstring_count'] - counts['non_english_docstring_count']
            english_data['Functions'] += counts['function_count'] - counts['non_english_function_count']
            english_data['Classes'] += counts['class_count'] - counts['non_english_class_count']
            english_data['Variables'] += counts['variable_count'] - counts['non_english_variable_count']
            english_data['Constants'] += counts['constant_count'] - counts['non_english_constant_count']
            
            # Non-English content
            non_english_data['Identifiers'] += counts['non_english_identifier_count']
            non_english_data['Comments'] += counts['non_english_comment_count']
            non_english_data['Docstrings'] += counts['non_english_docstring_count']
            non_english_data['Functions'] += counts['non_english_function_count']
            non_english_data['Classes'] += counts['non_english_class_count']
            non_english_data['Variables'] += counts['non_english_variable_count']
            non_english_data['Constants'] += counts['non_english_constant_count']
            non_english_data['Literals'] += counts['non_english_literal_count']
        
        total_english += sum(english_data.values())
        for k, v in non_english_data.items():
            categories[k] += v
            total_non_english += v
    
    # Create figure for overall statistics
    plt.figure(figsize=(12, 8))
    
    if total_english + total_non_english == 0:
        plt.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
        plt.title('Overall Content Distribution\n(No Data)', pad=20)
    else:
        # Main pie chart (English vs Non-English)
        main_sizes = [total_english, total_non_english]
        main_labels = [
            f'English\n({total_english/(total_english + total_non_english)*100:.1f}%)',
            f'Non-English\n({total_non_english/(total_english + total_non_english)*100:.1f}%)'
        ]
        colors = ['#66B2FF', '#FF9999']
        
        plt.pie(main_sizes, labels=main_labels, colors=colors, autopct='%1.1f%%',
                startangle=90, pctdistance=0.85)
        
        # Create a smaller circle at the center
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        # Add category breakdown in the center
        if total_non_english > 0:
            category_text = "Non-English Breakdown:\n"
            for category, value in categories.items():
                if value > 0:
                    percentage = (value / total_non_english) * 100
                    category_text += f"{category}: {percentage:.1f}%\n"
            plt.text(0, 0, category_text, ha='center', va='center', fontsize=8)
        
        plt.title('Overall Content Distribution', pad=20)
    
    output_path = os.path.join(output_folder, 'overall_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    try:
        # Ask for output folder name
        output_folder = input("Enter the name of the folder to save visualizations (default: 'visualization_results'): ").strip()
        if not output_folder:
            output_folder = 'visualization_results'
        
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        print(f"\nCreated output folder: {output_folder}")
        
        # Load the analysis results
        data = load_analysis_results()
        
        # Create visualizations for each repository
        create_repo_visualizations(data, output_folder)
        
        # Create overall pie chart
        create_overall_pie_chart(data, output_folder)
        
        print("\nVisualizations have been saved in the folder:", output_folder)
        print(f"- Individual repository analyses as '{output_folder}/repo_analysis_X.png'")
        print(f"- Overall distribution as '{output_folder}/overall_distribution.png'")
        
    except FileNotFoundError:
        print("Error: analysis_output.json file not found. Please make sure the file exists in the current directory.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in analysis_output.json file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Use 'Agg' backend to avoid Tcl/Tk issues
    import matplotlib
    matplotlib.use('Agg')
    main() 