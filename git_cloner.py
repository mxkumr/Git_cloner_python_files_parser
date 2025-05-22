import os
import tempfile
import subprocess
import json
import csv
from pathlib import Path

from python_code_parser import analyze_code  # Ensure this imports the updated version

REPO_LIST = [
    "https://github.com/leifengwl/MoGuDing-Auto",
    # Add more repos as needed
]

def clone_repo(url, destination):
    result = subprocess.run(["git", "clone", "--depth", "1", url, destination], capture_output=True)
    return result.returncode == 0

def find_py_files(repo_path):
    return list(Path(repo_path).rglob("*.py"))

def calculate_percentage(count, total):
    if total == 0:
        return 0
    return (count / total) * 100

def analyze_repo(url):
    print(f"\n🔽 Cloning: {url}")
    repo_results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        success = clone_repo(url, tmpdir)
        if not success:
            print(f"❌ Failed to clone {url}")
            return

        py_files = find_py_files(tmpdir)
        print(f"📂 Found {len(py_files)} Python files.")

        for py_file in py_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    code = f.read()
                result = analyze_code(code)

                # Calculate total occurrences of all categories for the percentage calculation
                total_occurrences = (result.keyword_count + result.identifier_count + result.literal_count +
                                   result.constant_count + result.comment_count + result.non_english_count)

                # Calculate the percentage for each category
                keyword_percentage = calculate_percentage(result.keyword_count, total_occurrences)
                identifier_percentage = calculate_percentage(result.identifier_count, total_occurrences)
                literal_percentage = calculate_percentage(result.literal_count, total_occurrences)
                constant_percentage = calculate_percentage(result.constant_count, total_occurrences)
                comment_percentage = calculate_percentage(result.comment_count, total_occurrences)
                non_english_percentage = calculate_percentage(result.non_english_count, total_occurrences)

                data = {
                    "repo_url": url,
                    "file_name": py_file.name,
                    "keywords": sorted(result.keywords),
                    "identifiers": sorted(result.identifiers),
                    "literals": sorted(result.literals),
                    "constants": sorted(result.constants),
                    "comments": sorted(result.comments),
                    "non_english": sorted(result.non_english),
                    "module_attrs": sorted(result.module_attrs),  # Added module attributes
                    "keyword_count": result.keyword_count,
                    "keyword_percentage": round(keyword_percentage, 2),
                    "identifier_count": result.identifier_count,
                    "identifier_percentage": round(identifier_percentage, 2),
                    "literal_count": result.literal_count,
                    "literal_percentage": round(literal_percentage, 2),
                    "constant_count": result.constant_count,
                    "constant_percentage": round(constant_percentage, 2),
                    "comment_count": result.comment_count,
                    "comment_percentage": round(comment_percentage, 2),
                    "non_english_count": result.non_english_count,
                    "non_english_percentage": round(non_english_percentage, 2)
                }
                repo_results.append(data)

                # Console preview with improved formatting
                print(f"\n📄 File: {py_file.name}")
                print("  🔑 Keywords ({}, {:.2f}%):".format(result.keyword_count, keyword_percentage))
                for kw in data["keywords"]:
                    print(f"      - {kw}")
                    
                print("  🆔 Identifiers ({}, {:.2f}%):".format(result.identifier_count, identifier_percentage))
                for id in data["identifiers"]:
                    print(f"      - {id}")
                    
                print("  📦 Module Attributes:")  # New section for module attributes
                for attr in data["module_attrs"]:
                    print(f"      - {attr}")
                    
                print("  🔤 Literals ({}, {:.2f}%):".format(result.literal_count, literal_percentage))
                for lit in data["literals"][:5]:  # Show first 5 literals to avoid cluttering
                    print(f"      - {lit}")
                if len(data["literals"]) > 5:
                    print(f"      ... and {len(data['literals']) - 5} more")
                    
                print("  🔢 Constants ({}, {:.2f}%):".format(result.constant_count, constant_percentage))
                for const in data["constants"]:
                    print(f"      - {const}")
                    
                print("  💬 Comments ({}, {:.2f}%):".format(result.comment_count, comment_percentage))
                for comment in data["comments"]:
                    print(f"      - {comment}")
                    
                print("  🌐 Non-English ({}, {:.2f}%):".format(result.non_english_count, non_english_percentage))
                for ne in data["non_english"]:
                    print(f"      - {ne}")

            except Exception as e:
                print(f"⚠️ Failed to parse {py_file}: {e}")

    # JSON Output
    json_file = "analysis_output.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(repo_results, f, ensure_ascii=False, indent=2)
    print(f"\n📝 JSON written to {json_file}")

    # CSV Output
    csv_file = "analysis_output.csv"
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "repo_url", "file_name", "keyword_count", "keyword_percentage", 
            "identifier_count", "identifier_percentage", "literal_count", 
            "literal_percentage", "constant_count", "constant_percentage", 
            "comment_count", "comment_percentage", "non_english_count", 
            "non_english_percentage", "keywords", "identifiers", "module_attrs",  # Added module_attrs
            "literals", "constants", "comments", "non_english"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in repo_results:
            writer.writerow({
                "repo_url": row["repo_url"],
                "file_name": row["file_name"],
                "keyword_count": row["keyword_count"],
                "keyword_percentage": row["keyword_percentage"],
                "identifier_count": row["identifier_count"],
                "identifier_percentage": row["identifier_percentage"],
                "literal_count": row["literal_count"],
                "literal_percentage": row["literal_percentage"],
                "constant_count": row["constant_count"],
                "constant_percentage": row["constant_percentage"],
                "comment_count": row["comment_count"],
                "comment_percentage": row["comment_percentage"],
                "non_english_count": row["non_english_count"],
                "non_english_percentage": row["non_english_percentage"],
                "keywords": ", ".join(row["keywords"]),
                "identifiers": ", ".join(row["identifiers"]),
                "module_attrs": ", ".join(row["module_attrs"]),  # Added module_attrs
                "literals": ", ".join(row["literals"]),
                "constants": ", ".join(row["constants"]),
                "comments": ", ".join(row["comments"]),
                "non_english": ", ".join(row["non_english"])
            })
    print(f"📄 CSV written to {csv_file}")

if __name__ == "__main__":
    for repo_url in REPO_LIST:
        if repo_url.strip():
            analyze_repo(repo_url)
