import os
import sys
import json
import csv
from git import Repo
from pathlib import Path
from python_code_parser import analyze_file

# List of repositories to analyze
REPO_LIST = [
    "https://github.com/fighting41love/funNLP",
    "https://github.com/d2l-ai/d2l-zh",
    "https://github.com/hankcs/HanLP",
    "https://github.com/fxsjy/jieba",
    "https://github.com/timqian/chinese-independent-blogs",
    "https://github.com/ymcui/Chinese-LLaMA-Alpaca",
    "https://github.com/subframe7536/maple-font/tree/chinese",
    "https://github.com/LlamaFamily/Llama-Chinese",
    "https://github.com/Embedding/Chinese-Word-Vectors",
    "https://github.com/EmbraceAGI/awesome-chatgpt-zh",
    "https://github.com/ymcui/Chinese-BERT-wwm",
    "https://github.com/MorvanZhou/Reinforcement-learning-with-tensorflow",
    "https://github.com/hoochanlon/hamulete",
    "https://github.com/nl8590687/ASRT_SpeechRecognition",
    "https://github.com/ymcui/Chinese-LLaMA-Alpaca-2",
    "https://github.com/wzpan/wukong-robot",
    "https://github.com/lancopku/pkuseg-python",
    "https://github.com/pengxiao-song/LaWGPT",
    "https://github.com/649453932/Chinese-Text-Classification-Pytorch",
    "https://github.com/tangqiaoboy/iOSBlogCN"
]

def calculate_percentage(count, total):
    """Calculate percentage with proper handling of zero division."""
    if total == 0:
        return 0
    return (count / total) * 100

def clone_repository(repo_url: str, target_dir: str) -> str:
    """
    Clone a GitHub repository to the target directory.
    Returns the path to the cloned repository.
    """
    try:
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Extract repository name from URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(target_dir, repo_name)
        
        # Clone the repository if it doesn't exist
        if not os.path.exists(repo_path):
            print(f"🔽 Cloning repository {repo_url}...")
            Repo.clone_from(repo_url, repo_path)
            print("✅ Repository cloned successfully!")
        else:
            print(f"📂 Repository already exists at {repo_path}")
            
        return repo_path
        
    except Exception as e:
        print(f"❌ Error cloning repository: {str(e)}")
        return None

def find_python_files(repo_path: str) -> list:
    """Find all Python files in the repository."""
    return list(Path(repo_path).rglob("*.py"))

def analyze_repository(repo_path: str) -> list:
    """
    Analyze all Python files in the repository.
    Returns a list of analysis results.
    """
    results = []
    python_files = find_python_files(repo_path)
    
    print(f"\n📂 Found {len(python_files)} Python files to analyze.")
    
    for file_path in python_files:
        try:
            print(f"\n📄 Analyzing {file_path.name}...")
            result = analyze_file(str(file_path))
            
            # Calculate total occurrences for percentage calculation
            total_occurrences = (result.keyword_count + result.identifier_count + 
                               result.literal_count + result.constant_count + 
                               result.comment_count + result.non_english_count)
            
            # Create result dictionary with percentages
            file_result = {
                'file_path': str(file_path.relative_to(repo_path)),
                'identifiers': list(result.identifiers),
                'functions': list(result.function_names),
                'classes': list(result.class_names),
                'variables': list(result.variables),
                'non_english': list(result.non_english),
                'module_attrs': list(result.module_attrs),
                'docstrings': list(result.docstrings),
                'comments': list(result.comments),
                'stats': {
                    'identifier_count': result.identifier_count,
                    'identifier_percentage': round(calculate_percentage(result.identifier_count, total_occurrences), 2),
                    'function_count': result.function_count,
                    'class_count': result.class_count,
                    'variable_count': result.variable_count,
                    'non_english_count': result.non_english_count,
                    'non_english_percentage': round(calculate_percentage(result.non_english_count, total_occurrences), 2),
                    'comment_count': result.comment_count,
                    'comment_percentage': round(calculate_percentage(result.comment_count, total_occurrences), 2),
                    'docstring_count': result.docstring_count
                }
            }
            results.append(file_result)
            
            # Print detailed analysis
            print(f"  🔧 Functions ({result.function_count}):", sorted(result.function_names))
            print(f"  📚 Classes ({result.class_count}):", sorted(result.class_names))
            print(f"  📝 Variables ({result.variable_count}):", sorted(result.variables))
            print(f"  🌐 Non-English ({result.non_english_count}, {file_result['stats']['non_english_percentage']}%):", sorted(result.non_english))
            print(f"  📦 Module Attributes:", sorted(result.module_attrs))
            
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {str(e)}")
            continue
    
    return results

def save_results(results: list, output_dir: str, repo_name: str):
    """Save analysis results to JSON and CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save detailed results to JSON
    json_path = os.path.join(output_dir, f"{repo_name}_analysis.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save summary to CSV
    csv_path = os.path.join(output_dir, f"{repo_name}_summary.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['File', 'Identifiers', 'Functions', 'Classes', 'Variables', 
                        'Non-English', 'Non-English %', 'Comments', 'Comment %', 'Docstrings'])
        
        for result in results:
            writer.writerow([
                result['file_path'],
                result['stats']['identifier_count'],
                result['stats']['function_count'],
                result['stats']['class_count'],
                result['stats']['variable_count'],
                result['stats']['non_english_count'],
                f"{result['stats']['non_english_percentage']}%",
                result['stats']['comment_count'],
                f"{result['stats']['comment_percentage']}%",
                result['stats']['docstring_count']
            ])
    
    print(f"\n📊 Results saved to:")
    print(f"  - JSON: {json_path}")
    print(f"  - CSV: {csv_path}")

def main():
    # Set up directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repos_dir = os.path.join(base_dir, "repos")
    results_dir = os.path.join(base_dir, "results")
    
    # Process each repository
    for repo_url in REPO_LIST:
        print(f"\n{'='*80}")
        print(f"Processing repository: {repo_url}")
        print(f"{'='*80}")
        
        # Clone repository
        repo_path = clone_repository(repo_url, repos_dir)
        if repo_path is None:
            print(f"Skipping analysis for {repo_url} due to cloning error")
            continue
            
        repo_name = os.path.basename(repo_path)
        
        # Analyze repository
        print("\n🔍 Starting repository analysis...")
        results = analyze_repository(repo_path)
        
        # Save results
        save_results(results, results_dir, repo_name)
        
        print(f"\n✅ Analysis complete for {repo_name}!")

if __name__ == "__main__":
    main() 