import os
import tempfile
import subprocess
import json
import csv
from pathlib import Path
import logging
from typing import Dict, List
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from python_code_parser import analyze_code  # Ensure this imports the updated version

REPO_LIST = [
    "https://github.com/lonePatient/awesome-pretrained-chinese-nlp-models",
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

class RepoStats:
    def __init__(self):
        self.total_repos = len(REPO_LIST)
        self.cloned_repos = 0
        self.failed_repos = 0
        self.repos_with_python = 0
        self.total_python_files = 0
        self.total_non_english_content = 0
        self.repo_details = defaultdict(lambda: {
            'cloned': False,
            'python_files': 0,
            'non_english_files': 0,
            'error': None
        })
        
    def add_repo(self, repo_url: str):
        pass  # Already initialized in defaultdict
        
    def mark_cloned(self, repo_url: str, success: bool, error: str = None):
        self.repo_details[repo_url]['cloned'] = success
        if success:
            self.cloned_repos += 1
        else:
            self.failed_repos += 1
            self.repo_details[repo_url]['error'] = error
            
    def add_python_file(self, repo_url: str, has_non_english: bool = False):
        self.repo_details[repo_url]['python_files'] += 1
        self.total_python_files += 1
        if self.repo_details[repo_url]['python_files'] == 1:
            self.repos_with_python += 1
        if has_non_english:
            self.repo_details[repo_url]['non_english_files'] += 1
            self.total_non_english_content += 1

def clone_repository(repo_url: str, temp_dir: str) -> tuple[bool, str]:
    """Clone a repository to a temporary directory."""
    try:
        # Fix URL if it contains /tree/ (which is not a valid git URL)
        if '/tree/' in repo_url:
            repo_url = repo_url.split('/tree/')[0]
            logger.info(f"Modified URL to: {repo_url}")
            
        subprocess.run(['git', 'clone', '--depth', '1', repo_url], 
                      cwd=temp_dir, 
                      check=True,
                      capture_output=True,
                      text=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, str(e.stderr)

def analyze_repo(repo_url: str, stats: RepoStats) -> Dict:
    """Analyze a single repository."""
    stats.add_repo(repo_url)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        success, error = clone_repository(repo_url, temp_dir)
        stats.mark_cloned(repo_url, success, error)
        
        if not success:
            logger.error(f"Failed to clone {repo_url}: {error}")
            return None
            
        repo_name = repo_url.split('/')[-1]
        repo_path = os.path.join(temp_dir, repo_name)
        
        results = {
            'repository': repo_url,
            'files': []
        }
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        analysis = analyze_code(content)
                        has_non_english = False
                        
                        # Check for non-English content in various fields
                        if analysis.non_english_count > 0:
                            has_non_english = True
                            
                        stats.add_python_file(repo_url, has_non_english)
                        
                        results['files'].append({
                            'file_path': os.path.relpath(file_path, repo_path),
                            'analysis': {
                                'keyword_count': analysis.keyword_count,
                                'identifier_count': analysis.identifier_count,
                                'literal_count': analysis.literal_count,
                                'constant_count': analysis.constant_count,
                                'comment_count': analysis.comment_count,
                                'non_english_count': analysis.non_english_count,
                                'function_count': analysis.function_count,
                                'class_count': analysis.class_count,
                                'variable_count': analysis.variable_count,
                                'docstring_count': analysis.docstring_count,
                                'has_non_english': has_non_english
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error analyzing {file_path}: {str(e)}")
                        
        return results

def write_summary(stats: RepoStats):
    """Write analysis summary to a separate file."""
    summary = {
        'summary_stats': {
            'total_repositories': stats.total_repos,
            'successfully_cloned': stats.cloned_repos,
            'failed_to_clone': stats.failed_repos,
            'repositories_with_python': stats.repos_with_python,
            'total_python_files': stats.total_python_files,
            'total_files_with_non_english': stats.total_non_english_content
        },
        'repository_details': {}
    }
    
    for repo_url, details in stats.repo_details.items():
        summary['repository_details'][repo_url] = {
            'cloned_successfully': details['cloned'],
            'python_files_count': details['python_files'],
            'non_english_files_count': details['non_english_files'],
            'error': details['error']
        }
        
    with open('analysis_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    logger.info("\n📊 Summary written to analysis_summary.json")

def print_summary(stats: RepoStats):
    """Print a detailed summary to console."""
    logger.info("==================================================")
    logger.info("REPOSITORY ANALYSIS SUMMARY")
    logger.info("==================================================")
    logger.info(f"Total repositories to process: {stats.total_repos}")
    logger.info(f"Successfully cloned: {stats.cloned_repos}")
    logger.info(f"Failed to clone: {stats.failed_repos}")
    logger.info(f"Repositories with Python files: {stats.repos_with_python}")
    logger.info(f"Total Python files analyzed: {stats.total_python_files}")
    logger.info(f"Total files with non-English content: {stats.total_non_english_content}")
    logger.info("\nRepository Details:")
    
    for repo_url, details in stats.repo_details.items():
        logger.info(f"\n{repo_url}:")
        logger.info(f"  - Cloned successfully: {details['cloned']}")
        logger.info(f"  - Python files: {details['python_files']}")
        logger.info(f"  - Files with non-English content: {details['non_english_files']}")
        if details['error']:
            logger.info(f"  - Error: {details['error']}")
            
    logger.info("==================================================")

if __name__ == "__main__":
    all_results = []
    stats = RepoStats()
    
    for repo_url in REPO_LIST:
        if repo_url.strip():
            try:
                results = analyze_repo(repo_url, stats)
                if results:
                    all_results.append(results)
            except Exception as e:
                logger.error(f"Error processing repository {repo_url}: {str(e)}")
                
    # Write detailed results to JSON
    output = {
        'summary': {
            'total_repositories': stats.total_repos,
            'successfully_cloned': stats.cloned_repos,
            'failed_to_clone': stats.failed_repos,
            'repositories_with_python': stats.repos_with_python,
            'total_python_files': stats.total_python_files,
            'total_files_with_non_english': stats.total_non_english_content,
            'repository_details': {
                url: {
                    'cloned': details['cloned'],
                    'python_files': details['python_files'],
                    'non_english_files': details['non_english_files'],
                    'error': details['error']
                }
                for url, details in stats.repo_details.items()
            }
        },
        'analysis_results': all_results
    }
    
    with open('analysis_output.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    logger.info("📝 JSON written to analysis_output.json")
    
    # Write and print summary
    write_summary(stats)
    print_summary(stats)
