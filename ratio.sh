#!/bin/bash

# A simple bash script to calculate the deduplication ratio of two files.
# The first file is the original, and the second is the deduplicated file.

# Check if the correct number of arguments (2 files) is provided.
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <original_file> <deduplicated_file>"
    exit 1
fi

original_file="$1"
deduplicated_file="$2"

# Check if both files exist and are regular files.
if [ ! -f "$original_file" ]; then
    echo "Error: Original file '$original_file' not found."
    exit 1
fi

if [ ! -f "$deduplicated_file" ]; then
    echo "Error: Deduplicated file '$deduplicated_file' not found."
    exit 1
fi

# Get the size of the original file in bytes.
# The 'stat' command is used with the format string '%s' to get the size in bytes.
original_size=$(stat -c%s "$original_file")

# Get the size of the deduplicated file in bytes.
deduplicated_size=$(stat -c%s "$deduplicated_file")

# Check for zero division to avoid errors.
if [ "$deduplicated_size" -eq 0 ]; then
    echo "Error: The deduplicated file size is 0 bytes, cannot calculate ratio."
    exit 1
fi

# Calculate the deduplication ratio.
# The ratio is (Original Size / Deduplicated Size).
# Use 'bc' for floating-point arithmetic. The scale=2 sets the decimal precision to 2.
ratio=$(echo "scale=2; $original_size / $deduplicated_size" | bc)

# Print the results.
echo "Original File: $original_file ($original_size bytes)"
echo "Deduplicated File: $deduplicated_file ($deduplicated_size bytes)"
echo "Deduplication Ratio: ${ratio}:1"
