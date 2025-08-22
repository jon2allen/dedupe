#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A command-line tool to analyze files for duplicate data chunks and report
on potential space savings through deduplication.
"""

import argparse
import glob
from collections import defaultdict
import os

def analyze_files(file_glob, chunk_size, limit):
    """
    Analyzes files to find duplicate chunks.

    Args:
        file_glob (str): A glob pattern to match files.
        chunk_size (int): The size of each chunk in bytes.
        limit (int): The number of top duplicate chunks to report. 0 for all.
    """
    chunk_counts = defaultdict(int)
    chunk_bytes = defaultdict(int)

    print(f"[*] Starting analysis with chunk size: {chunk_size} bytes")
    print(f"[*] Searching for files with pattern: {file_glob}\n")

    files_to_process = glob.glob(file_glob, recursive=True)
    # Filter out directories from the glob results
    files_to_process = [f for f in files_to_process if os.path.isfile(f)]

    if not files_to_process:
        print("[!] No files found matching the pattern. Exiting.")
        return

    print(f"[*] Found {len(files_to_process)} files to process.")
    total_original_size = sum(os.path.getsize(f) for f in files_to_process)

    for filepath in files_to_process:
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    # We only count full-sized chunks for accurate stats,
                    # as partial chunks at the end of files can skew the ratio.
                    if len(chunk) == chunk_size:
                        chunk_counts[chunk] += 1
                        chunk_bytes[chunk] = len(chunk)
        except IOError as e:
            print(f"[!] Error reading file {filepath}: {e}")
        except Exception as e:
            print(f"[!] An unexpected error occurred with file {filepath}: {e}")

    # --- Analysis ---
    if not chunk_counts:
        print("\n--- Analysis Complete ---")
        print("No full-sized chunks found to analyze. Try a smaller chunk size.")
        return

    # Filter for chunks that appear more than once
    duplicate_chunks = {chunk: count for chunk, count in chunk_counts.items() if count > 1}

    if not duplicate_chunks:
        print("\n--- Analysis Complete ---")
        print("No duplicate chunks found. Your data is unique at this chunk size!")
        return

    # Calculate savings for each duplicate chunk
    # Savings = (count - 1) * chunk_size
    chunk_savings = {
        chunk: (count - 1) * chunk_bytes[chunk]
        for chunk, count in duplicate_chunks.items()
    }

    # Sort chunks by the potential savings in descending order
    sorted_chunks = sorted(
        chunk_savings.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # --- Reporting ---
    print("\n--- Deduplication Report ---")
    total_chunks_processed = sum(chunk_counts.values())
    unique_chunks_count = len(chunk_counts)
    duplicate_chunks_count = len(duplicate_chunks)
    total_potential_savings = sum(chunk_savings.values())

    # Calculate deduplication ratio
    size_after_dedupe = unique_chunks_count * chunk_size
    dedupe_ratio = total_original_size / size_after_dedupe if size_after_dedupe > 0 else 1.0

    print(f"\nSummary:")
    print(f"  - Total Files Analyzed: {len(files_to_process)}")
    print(f"  - Total Original Size: {total_original_size / 1024:.2f} KB ({total_original_size} bytes)")
    print(f"  - Chunk Size: {chunk_size} bytes")
    print(f"  - Total Chunks Processed: {total_chunks_processed}")
    print(f"  - Unique Chunks Found: {unique_chunks_count}")
    print(f"  - Size After Dedupe: {size_after_dedupe / 1024:.2f} KB ({size_after_dedupe} bytes)")
    print(f"  - Duplicate Chunks Found: {duplicate_chunks_count}")
    print(f"  - Total Potential Savings: {total_potential_savings / 1024:.2f} KB ({total_potential_savings} bytes)")
    print(f"  - Deduplication Ratio: {dedupe_ratio:.2f}:1")

    # Determine the limit for the report
    report_limit = len(sorted_chunks) if limit == 0 else min(limit, len(sorted_chunks))

    print(f"\nTop {report_limit} Duplicate Chunks by Potential Savings:")
    print("-" * 70)
    print(f"{'Rank':<5} | {'Chunk Hash (first 16 chars)':<30} | {'Count':<10} | {'Savings (Bytes)':<20}")
    print("-" * 70)

    for i, (chunk, savings) in enumerate(sorted_chunks[:report_limit]):
        # Represent the binary chunk with a portion of its hex representation
        chunk_repr = chunk.hex()[:16] + '...'
        count = chunk_counts[chunk]
        rank = i + 1
        print(f"{rank:<5} | {chunk_repr:<30} | {count:<10} | {savings:<20}")

    print("-" * 70)


def main():
    """Main function to parse arguments and run the analysis."""
    parser = argparse.ArgumentParser(
        description="A CLI tool to find duplicate data chunks in files and report potential savings.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "glob_pattern",
        type=str,
        help="Glob pattern to select files for analysis (e.g., '*.txt', 'data/**/*.log').\n"
             "Use quotes to avoid shell expansion."
    )
    parser.add_argument(
        "--chunk",
        dest="chunk_size",
        type=int,
        default=4096,
        help="The fixed size of chunks in bytes. Default is 4096 (4KB)."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Limit the report to the top N duplicate chunks. Use 0 to show all. Default is 50."
    )

    args = parser.parse_args()

    if args.chunk_size <= 0:
        print("[!] Error: Chunk size must be a positive integer.")
        return

    analyze_files(args.glob_pattern, args.chunk_size, args.limit)

if __name__ == "__main__":
    main()

