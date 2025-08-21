#!/usr/bin/env python3
import argparse
import glob
from collections import defaultdict
import os

def analyze_files(file_glob, limit):
    """
    Analyzes a collection of text files to find duplicate sentences and calculate
    potential deduplication savings.

    Args:
        file_glob (str): A glob pattern to match input files (e.g., "*.txt").
        limit (int): The number of top duplicate sentences to display in the report.
                     If 0, all unique sentences are shown.
    """
    # Use a defaultdict to easily handle counting and byte storage
    # The structure will be: {sentence: {'count': N, 'bytes': M}}
    sentence_stats = defaultdict(lambda: {'count': 0, 'bytes': 0})
    
    total_bytes_processed = 0
    total_sentences = 0
    files_processed = 0

    # Expand the glob pattern to get a list of file paths
    file_paths = glob.glob(file_glob)
    if not file_paths:
        print(f"Error: No files found matching the pattern: {file_glob}")
        return

    for file_path in file_paths:
        # Ensure we are only processing files, not directories
        if not os.path.isfile(file_path):
            continue
            
        files_processed += 1
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Treat each line as a sentence
                    sentence = line.strip()
                    if not sentence:
                        continue # Skip empty lines

                    total_sentences += 1
                    
                    # Encode to get the byte size, as strings in Python are abstract
                    sentence_bytes = len(sentence.encode('utf-8'))
                    total_bytes_processed += sentence_bytes
                    
                    # Update stats for this sentence
                    sentence_stats[sentence]['count'] += 1
                    # Store the byte size of a single instance of the sentence
                    if sentence_stats[sentence]['bytes'] == 0:
                        sentence_stats[sentence]['bytes'] = sentence_bytes
        except Exception as e:
            print(f"Could not read file {file_path}: {e}")

    # --- Calculations for the report ---
    
    # Sort sentences by frequency (most common first)
    # The key is a lambda function that accesses the 'count' for each sentence
    sorted_sentences = sorted(
        sentence_stats.items(), 
        key=lambda item: item[1]['count'], 
        reverse=True
    )

    unique_sentences_count = len(sentence_stats)
    
    # Calculate the size if all sentences were stored uniquely
    deduplicated_size = sum(item[1]['bytes'] for item in sentence_stats.items())
    
    # Calculate potential savings
    bytes_saved = total_bytes_processed - deduplicated_size
    
    # Calculate deduplication factor
    if deduplicated_size > 0:
        dedupe_factor = total_bytes_processed / deduplicated_size
    else:
        dedupe_factor = 0

    # --- Generate and print the report ---
    
    print("\n--- Deduplication Analysis Report ---")
    print(f"Files Processed: {files_processed}")
    print(f"Total Bytes Processed: {total_bytes_processed:,} bytes")
    print(f"Total Sentences/Lines: {total_sentences:,}")
    print(f"Unique Sentences/Lines: {unique_sentences_count:,}")
    
    print("\n--- Potential Savings ---")
    print(f"Potential Reduction: {bytes_saved:,} bytes")
    print(f"Deduplication Factor: {dedupe_factor:.2f}x")
    print("(This means the original data is ~{:.2f} times larger than the unique data)".format(dedupe_factor))

    # Determine how many top sentences to show based on the limit
    if limit == 0:
        # If limit is 0, show all unique sentences
        display_limit = len(sorted_sentences)
        report_title = "All Unique Sentences/Phrases by Frequency"
    else:
        # Otherwise, show the top N, or fewer if there aren't that many
        display_limit = min(limit, len(sorted_sentences))
        report_title = f"Top {display_limit} Unique Sentences/Phrases by Frequency"

    print(f"\n--- {report_title} ---")
    
    if not sorted_sentences:
        print("No sentences found to display.")
        return
        
    # Print table header
    print(f"{'Rank':<5} | {'Count':<10} | {'Bytes (Single)':<15} | {'Bytes (Total)':<15} | {'Sentence/Phrase'}")
    print("-" * 80)

    # Print the top sentences
    for i, (sentence, stats) in enumerate(sorted_sentences[:display_limit]):
        rank = i + 1
        count = stats['count']
        single_bytes = stats['bytes']
        total_bytes = count * single_bytes
        # Truncate long sentences for display purposes
        display_sentence = (sentence[:70] + '...') if len(sentence) > 73 else sentence
        
        print(f"{rank:<5} | {count:<10,} | {single_bytes:<15,} | {total_bytes:<15,} | \"{display_sentence}\"")

def main():
    """Main function to parse arguments and run the analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze text files for duplicate sentences and report potential deduplication savings.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "file_glob",
        type=str,
        help="Glob pattern for input files (e.g., 'data/*.txt').\n"
             "Remember to quote the pattern to prevent shell expansion."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of top duplicate sentences to show in the report.\n"
             "Use 0 to display all unique sentences. (Default: 50)"
    )
    args = parser.parse_args()
    
    analyze_files(args.file_glob, args.limit)

if __name__ == "__main__":
    main()

