import argparse
import glob
import gzip
import os
import pickle
import sys
from typing import Dict

try:
    import xxhash
except ImportError:
    print("Error: The 'xxhash' library is not installed.")
    print("Please install it using: pip install xxhash")
    sys.exit(1)


class HashStore:
    """
    Manages the persistent storage of unique strings and their xxhash32 hashes.

    This class handles loading from and saving to a compressed binary file.
    It uses a dictionary to map hash hex strings to the original text.
    It includes a crucial check for hash collisions.
    """

    def __init__(self, db_path: str):
        """Initializes the HashStore and loads the database from a file."""
        self.db_path = db_path
        self.store: Dict[str, str] = {}
        self._load()

    def _load(self):
        """Loads the hash store from a gzipped pickle file if it exists."""
        if os.path.exists(self.db_path):
            try:
                with gzip.open(self.db_path, 'rb') as f:
                    self.store = pickle.load(f)
                print(f"Successfully loaded hash store from '{self.db_path}'.")
            except (IOError, pickle.UnpicklingError) as e:
                print(f"Warning: Could not load data from '{self.db_path}'. Creating a new empty store. Error: {e}")
                self.store = {}
        else:
            print(f"No existing hash store found at '{self.db_path}'. A new store will be created on save.")

    def save(self):
        """Saves the current hash store to a gzipped pickle file."""
        try:
            with gzip.open(self.db_path, 'wb') as f:
                pickle.dump(self.store, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Successfully saved hash store to '{self.db_path}'.")
        except IOError as e:
            print(f"Error: Could not save hash store to '{self.db_path}'. Error: {e}")
            sys.exit(1)

    def add_item(self, xxhash_obj: xxhash.xxh32, text: str) -> bool:
        """
        Adds a new unique string to the store.

        This method checks for hash collisions. If a hash exists but the
        corresponding string is different, a warning is printed and the
        new string is not added.

        Args:
            xxhash_obj: An xxhash.xxh32 object containing the hash.
            text: The original, case-sensitive string.

        Returns:
            True if the item was added, False otherwise.
        """
        hash_hex = xxhash_obj.hexdigest()
        if hash_hex in self.store:
            # Check for a real collision (different strings, same hash)
            if self.store[hash_hex] != text:
                print(f"Warning: Hash collision detected for hex '{hash_hex}'. "
                      f"Original: '{self.store[hash_hex]}', New: '{text}'. "
                      "New item ignored.")
            return False
        else:
            self.store[hash_hex] = text
            return True


class DedupeEngine:
    """
    Contains the core logic for processing and deduplicating text files.

    This class works with a HashStore instance to manage unique lines of text
    and handles the encoding and decoding of files using xxhash.
    """
    def __init__(self, hash_store: HashStore):
        """Initializes the DedupeEngine with a HashStore instance."""
        self.hash_store = hash_store

    def seed_from_glob(self, glob_pattern: str):
        """
        Reads files matching a glob pattern and adds unique lines to the store.
        This is a memory-efficient, line-by-line process.
        """
        files = glob.glob(glob_pattern)
        if not files:
            print(f"No files found matching glob pattern '{glob_pattern}'.")
            return

        unique_lines_added = 0
        total_lines_processed = 0
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                    print(f"Processing file: {filepath}")
                    for line in infile:
                        total_lines_processed += 1
                        line = line.rstrip('\n')
                        if line:
                            # Use xxhash32 for a 4-byte hash
                            h = xxhash.xxh32(line, seed=0)
                            if self.hash_store.add_item(h, line):
                                unique_lines_added += 1
            except IOError as e:
                print(f"Error processing file '{filepath}': {e}")
                continue

        print(f"\nSeeding complete.")
        print(f"Total lines processed: {total_lines_processed}")
        print(f"New unique lines added to store: {unique_lines_added}")

    def process_and_encode(self, input_file: str, output_file: str):
        """
        Reads an input file, deduplicates lines, and encodes them into a
        compact binary file.
        """
        if not os.path.exists(input_file):
            print(f"Error: Input file not found at '{input_file}'.")
            sys.exit(1)

        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
                with open(output_file, 'wb') as outfile:
                    print(f"Encoding '{input_file}' to '{output_file}'...")
                    for line in infile:
                        line = line.rstrip('\n')
                        if not line:
                            # Write the special single-byte marker for blank lines
                            outfile.write(b'\x00')
                        else:
                            # Hash the line and add it to the store if it's new
                            h = xxhash.xxh32(line, seed=0)
                            self.hash_store.add_item(h, line)
                            # Write the raw 4-byte hash to the output file
                            outfile.write(h.digest())
            print("Encoding complete.")
        except IOError as e:
            print(f"Error during file processing: {e}")
            sys.exit(1)

    def decode_and_print(self, hash_file: str):
        """
        Reads a binary file of hashes and prints the original strings
        by looking them up in the hash store.
        """
        if not os.path.exists(hash_file):
            print(f"Error: Hash file not found at '{hash_file}'.")
            sys.exit(1)

        try:
            with open(hash_file, 'rb') as infile:
                print(f"Decoding '{hash_file}'...")
                while True:
                    # Read one byte to check for the blank line marker
                    chunk = infile.read(1)
                    if not chunk:
                        # EOF
                        break
                    
                    if chunk == b'\x00':
                        # Special marker found, print a newline
                        print()
                    else:
                        # It's not a marker, so it's the first byte of a hash
                        remaining_hash_bytes = infile.read(3)
                        if len(remaining_hash_bytes) != 3:
                            print("\nWarning: Incomplete hash block found at the end of the file. Stopping decode.")
                            break
                        
                        full_hash_bytes = chunk + remaining_hash_bytes
                        hash_hex_key = full_hash_bytes.hex()
                        
                        if hash_hex_key in self.hash_store.store:
                            print(self.hash_store.store[hash_hex_key])
                        else:
                            print(f"\nWarning: Hash '{hash_hex_key}' not found in the database. "
                                  "The original line cannot be restored. "
                                  "The file may have been created with a different database.")
            print("\nDecoding complete.")
        except IOError as e:
            print(f"Error during file decoding: {e}")
            sys.exit(1)


def main():
    """Main function to parse arguments and run the tool."""
    parser = argparse.ArgumentParser(
        description="A memory-efficient text deduplication and encoding tool.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--db",
        type=str,
        default="dedupe_main.db",
        help="Path for the hash store database file. Defaults to 'dedupe_main.db'."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--seed",
        type=str,
        help="Glob pattern to find files to seed the hash database (e.g., 'data/*.txt')."
    )
    group.add_argument(
        "--input",
        type=str,
        help="Path to an input text file for deduplication and encoding."
    )
    group.add_argument(
        "--decode",
        type=str,
        help="Path to a binary hash file to decode back to text."
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Path to the output binary file for encoded data. "
             "Required when using --input."
    )

    args = parser.parse_args()

    # Create the hash store and engine
    hash_store = HashStore(args.db)
    dedupe_engine = DedupeEngine(hash_store)

    # Process the requested command
    if args.seed:
        dedupe_engine.seed_from_glob(args.seed)
    elif args.input:
        if not args.output:
            parser.error("--output is required when using --input.")
        dedupe_engine.process_and_encode(args.input, args.output)
    elif args.decode:
        dedupe_engine.decode_and_print(args.decode)

    # Save the database at the end of any successful operation
    hash_store.save()


if __name__ == "__main__":
    main()
