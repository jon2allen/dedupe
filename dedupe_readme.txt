Sentence Deduplication Proof of Concept
This project demonstrates and tests different Python-based tools for sentence-level deduplication. The included run_tests.sh script automates the full workflow for a proof of concept, including data seeding, deduplication, result analysis, and cleanup.

Prerequisites
This script assumes the following file structure and dependencies are in place:

A data directory containing the ANZ535.tgz archive.

The three deduplication tools: collision_dedup_cli.py, dedupe_cli.py, and final_dedupe_cli.py.

A ratio analysis utility: ratio.sh.

Python 3 installed on your system.

Workflow
The run_tests.sh script automates the entire process from start to finish. You should execute it from the project's root directory.

./run_tests.sh

The script performs the following actions in sequence for each of the three deduplication programs:

Setup: It begins by untarring the ANZ535.tgz file into the data directory.

Seeding: It seeds a temporary database named dedupe_main.db using all the .txt files in the data directory. This process populates the database with sentences from the source material.

Deduplication: For a set of example files (ftestin1.txt, testin2.txt, testin.txt), the script runs the deduplication tool to remove any duplicate sentences. The unique sentences are saved to a new file with a .dat extension.

Analysis: The ratio.sh utility is run to compare the size of the original input file against the deduplicated .dat output file, providing a measure of the deduplication efficiency.

Decoding: The unique sentences are then decoded from the .dat file back into a human-readable format.

Cleanup: After each program is tested, the dedupe_main.db database is deleted to ensure a clean slate for the next test. A final cleanup step removes all generated .txt files from the data directory.

The script provides a detailed log of each step as it runs, helping you track the progress and results of each deduplication tool.
