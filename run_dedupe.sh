#!/bin/bash

# This script automates the testing of three different deduplication tools.
# It performs seeding, deduplication, ratio analysis, and decoding for each tool
# and then cleans up the generated database and files.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 1. Initial Setup: Untarring the file ---
echo "--- Initializing setup... ---"

# Save the current directory to return to later
initial_dir=$(pwd)

# Define the data directory and the seed glob pattern
data_dir="data"
seed_glob_pattern="./data/*.txt"
tgz_file="ANZ535.tgz"

# Change to the data directory
echo "Changing directory to $data_dir..."
cd "$data_dir"

# Untar the specified file.
echo "Untarring $tgz_file..."
tar -xvzf "$tgz_file"

# Change back to the initial directory
echo "Changing directory back to $initial_dir..."
cd "$initial_dir"

# --- 2. Define programs and example files ---
programs=("collision_dedup_cli.py" "dedupe_cli.py" "final_dedupe_cli.py")
example_files=("ftestin1.txt" "testin2.txt" "testin.txt")

# --- 3. Main Loop: Iterate through each program ---
for program in "${programs[@]}"; do
    echo "======================================================"
    echo "--- Testing program: $program ---"
    
    # Check if the program exists before proceeding
    if [ ! -f "$program" ]; then
        echo "Error: $program not found. Skipping to the next program."
        continue
    fi

    # --- 3.1 Seed the database ---
    echo "--- Seeding the database from $seed_glob_pattern ---"
    python3 "$program" --seed "$seed_glob_pattern"
    
    # --- 3.2 Iterate through each example file for processing ---
    for example_file in "${example_files[@]}"; do
        echo "------------------------------------------------------"
        echo "Processing example file: $example_file"
        
        # Create a unique output file name with .dat extension
        output_file="${example_file%.txt}.dat"

        # Run the deduplication tool on the input file
        echo "Running deduplication on $example_file, output to $output_file"
        python3 "$program" --input "$example_file" --output "$output_file"

        # --- 3.3 Run ratio.sh on original and output files ---
        echo "Running ratio utility on original and output files"
        ./ratio.sh "$example_file" "$output_file"

        # --- 3.4 Decode the unique .dat file ---
        echo "Decoding the output file: $output_file"
        python3 "$program" --decode "$output_file"
    done
    
    # --- 3.5 Delete the database file ---
    echo "--- Deleting the database: dedupe_main.db ---"
    rm dedupe_main.db
    
    echo "--- Test for $program complete. ---"
done

# --- 4. Final Cleanup ---
echo "--- Final Cleanup: Removing *.txt files from the data directory ---"
cd "$data_dir"
rm *.txt

# Change back to the initial directory and report finished
cd "$initial_dir"
echo "--- All deduplication tests and cleanup operations finished. ---"
echo "======================================================"
