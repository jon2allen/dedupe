#!/usr/bin/env python3
import argparse
import glob
import re
from collections import Counter
import os

def analyze_files(file_glob):
    """
    Analyzes files matching a glob pattern to find duplicate words and calculate
    potential deduplication savings.

    Args:
        file_glob (str): A glob pattern for the input files (e.g., '*.txt').

    Returns:
        dict: A dictionary containing the analysis results.
    """
    word_counter = Counter()
    total_words = 0
    total_bytes_original = 0
    processed_files = []

    # Find all files matching the glob pattern
    files = glob.glob(file_glob)
    if not files:
        print(f"Error: No files found matching the pattern: {file_glob}")
        return None

    for file_path in files:
        # Check if it's a file and not a directory
        if not os.path.isfile(file_path):
            continue
        
        processed_files.append(os.path.basename(file_path))
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Simple word tokenization: lowercase and split by non-alphanumeric characters
                words = re.findall(r'\b\w+\b', content.lower())
                
                for word in words:
                    word_counter[word] += 1
                    total_bytes_original += len(word.encode('utf-8'))
                
                total_words += len(words)

        except Exception as e:
            print(f"Could not read or process file {file_path}: {e}")
            continue

    if not word_counter:
        print("No words were found in the processed files.")
        return None

    # --- Calculate Deduplication Stats ---
    unique_words = list(word_counter.keys())
    num_unique_words = len(unique_words)
    
    # Calculate the size if we only stored each unique word once
    total_bytes_deduplicated = sum(len(word.encode('utf-8')) for word in unique_words)

    # For a true deduplication system, you'd also need pointers/references.
    # We'll estimate this as a small overhead per word occurrence.
    # Let's assume a 4-byte pointer for each word instance.
    pointer_size = 4 
    total_bytes_with_pointers = total_bytes_deduplicated + (total_words * pointer_size)

    bytes_saved = total_bytes_original - total_bytes_with_pointers
    
    # Handle division by zero
    if total_bytes_with_pointers > 0:
        deduplication_factor = total_bytes_original / total_bytes_with_pointers
    else:
        deduplication_factor = 0

    # Get the top 50 most common words
    top_50_words = word_counter.most_common(50)

    return {
        "processed_files": processed_files,
        "total_words": total_words,
        "unique_words": num_unique_words,
        "total_bytes_original": total_bytes_original,
        "total_bytes_deduplicated_storage": total_bytes_deduplicated,
        "total_bytes_with_pointers": total_bytes_with_pointers,
        "bytes_saved": bytes_saved,
        "deduplication_factor": deduplication_factor,
        "top_50_words": top_50_words
    }

def print_report(results):
    """
    Prints a formatted summary report of the analysis.
    """
    if not results:
        return

    print("\n--- Deduplication Analysis Report ---")
    print(f"Processed Files: {', '.join(results['processed_files'])}")
    print("-" * 35)
    
    print("\n--- Overall Statistics ---")
    print(f"Total Words Analyzed: {results['total_words']:,}")
    print(f"Unique Words Found:   {results['unique_words']:,}")
    print("-" * 35)

    print("\n--- Deduplication Potential ---")
    print(f"Original Size (sum of all word bytes): {results['total_bytes_original'] / 1024:,.2f} KB")
    print(f"Deduplicated Size (unique words + pointers): {results['total_bytes_with_pointers'] / 1024:,.2f} KB")
    print(f"Potential Bytes Saved: {results['bytes_saved'] / 1024:,.2f} KB")
    print(f"Potential Deduplication Factor: {results['deduplication_factor']:.2f}x")
    reduction_percentage = (results['bytes_saved'] / results['total_bytes_original']) * 100 if results['total_bytes_original'] > 0 else 0
    print(f"Potential Space Reduction: {reduction_percentage:.2f}%")
    print("-" * 35)

    print("\n--- Top 50 Most Frequent Words ---")
    print(f"{'Rank':<5} {'Word':<20} {'Frequency':<15} {'Bytes/Word':<12}")
    print(f"{'-'*4:<5} {'-'*19:<20} {'-'*14:<15} {'-'*11:<12}")
    for i, (word, count) in enumerate(results['top_50_words'], 1):
        byte_size = len(word.encode('utf-8'))
        print(f"{i:<5} {word:<20} {count:<15,} {byte_size:<12}")
    print("-" * 35)


def main():
    """
    Main function to parse command-line arguments and run the analysis.
    """
    parser = argparse.ArgumentParser(
        description="Analyze text files for word duplication and calculate potential savings.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "file_glob",
        type=str,
        help="A glob pattern to select files for analysis (e.g., 'data/*.txt').\n"
             "Make sure to wrap it in quotes if it contains wildcards."
    )
    
    args = parser.parse_args()
    
    results = analyze_files(args.file_glob)
    if results:
        print_report(results)

if __name__ == "__main__":
    main()

