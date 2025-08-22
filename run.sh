#!/bin/bash

# This script first navigates to a data directory, extracts a compressed file,
# and then returns to the original directory to run a series of deduplication
# analysis commands with different parameters.

# --- Configuration ---
# Set the base directory for the python scripts. We assume the script is run
# from a parent directory where the python scripts are located.
SCRIPT_DIR="./"

# Set the data directory where the compressed file is located and where the
# analysis will be performed.
DATA_DIR="./data/"

# Set the name of the compressed file to extract.
TAR_FILE="ANZ535.tgz"

# Set the common limit for the analysis.
LIMIT=50

# --- Directory and File Operations ---
echo "Moving to data directory and extracting files..."

# Use pushd and popd to easily change to and from the data directory.
# This saves the current directory to a stack and changes to the new one.
pushd "${DATA_DIR}"

# Extract the compressed file. The -x flag is for extract, -v for verbose
# (shows progress), -z for gzip compression, and -f for file.
tar -xzf "${TAR_FILE}"

# Return to the previous directory in the stack.
popd

echo "Directory change and extraction complete."
echo "-----------------------------------"

# --- Analysis Commands ---
# Now, run the analysis scripts from the original location, using the variable
# for the data directory path.

# Run the first command
echo "Running dedupe_analzyer.py..."
${SCRIPT_DIR}dedupe_analzyer.py --limit ${LIMIT} "${DATA_DIR}*.txt"
echo "-----------------------------------"

# Run the next command for sentence-level analysis
echo "Running dedupe_analzyer_sentence.py..."
${SCRIPT_DIR}dedupe_analzyer_sentence.py --limit ${LIMIT} "${DATA_DIR}*.txt"
echo "-----------------------------------"

# Run the chunk-based analysis with different chunk sizes
echo "Running dedupe_analyzer_chunk.py with various chunk sizes..."

# Chunk size 1024
echo "Chunk size: 1024"
# NOTE: The original command used a slightly different data path, but this has been
# standardized to match the directory that was untarred.
${SCRIPT_DIR}dedupe_analyzer_chunk.py --chunk 1024 --limit ${LIMIT} "${DATA_DIR}*.txt"
echo "---"

# Chunk size 2048
echo "Chunk size: 2048"
${SCRIPT_DIR}dedupe_analyzer_chunk.py --chunk 2048 --limit ${LIMIT} "${DATA_DIR}*.txt"
echo "---"

# Chunk size 256
echo "Chunk size: 256"
${SCRIPT_DIR}dedupe_analyzer_chunk.py --chunk 256 --limit ${LIMIT} "${DATA_DIR}*.txt"
echo "---"

# Chunk size 128
echo "Chunk size: 128"
${SCRIPT_DIR}dedupe_analyzer_chunk.py --chunk 128 --limit ${LIMIT} "${DATA_DIR}*.txt"
echo "---"

echo "Script complete."

# --- Cleanup ---
echo "Cleaning up extracted .txt files..."
# Move to the data directory
pushd "${DATA_DIR}" > /dev/null

# Remove all files with the .txt extension.
# The > /dev/null redirects stdout to a null device to suppress the output of the command.
echo "cleaning up txt files in data directory"
rm  *.txt

# Return to the previous directory
popd > /dev/null

echo "Cleanup complete."
echo "Script finished."


