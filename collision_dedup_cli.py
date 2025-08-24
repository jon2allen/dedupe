import argparse
import hashlib
import pickle
import gzip
import os
import glob
import sys
from typing import Set, IO, Union, Tuple, Dict

# --- Core Logic Classes (provided by user) ---

class HashStore:
    """
    Manages the storage of unique items by mapping a hash to the original string.
    Handles serialization to a compressed blob file.
    """

    def __init__(self, blob_path: str = 'dedupe_store.pkl.gz'):
        """
        Initializes the HashStore.

        Args:
            blob_path (str): The path to store the compressed data blob.
        """
        # The dictionary will store: { hash: original_string }
        self.items: Dict[str, str] = {}
        self.blob_path = blob_path
        self._load_store()

    def add_item(self, item_hash: str, original_string: str) -> bool:
        """
        Adds an item (hash and original string) to the store if the hash is not already present.
        If a hash collision is detected, a warning is printed.

        Args:
            item_hash (str): The hash of the string.
            original_string (str): The original string to store.

        Returns:
            bool: True if the item was new and added, False otherwise.
        """
        if item_hash in self.items:
            # Check for a hash collision (different string, same hash)
            if self.items[item_hash] != original_string:
                print(f"WARNING: Hash collision detected! The following string was ignored:")
                print(f"  Hash: '{item_hash}'")
                print(f"  Existing string: '{self.items[item_hash]}'")
                print(f"  Ignored string:  '{original_string}'")
            return False
        else:
            self.items[item_hash] = original_string
            return True

    def get_string_by_hash(self, item_hash: str) -> Union[str, None]:
        """
        Retrieves the original string for a given hash.

        Args:
            item_hash (str): The hash to look up.

        Returns:
            Union[str, None]: The original string if found, otherwise None.
        """
        return self.items.get(item_hash)

    def _load_store(self):
        """Loads the hash-to-string dictionary from the blob file if it exists."""
        if os.path.exists(self.blob_path):
            try:
                with gzip.open(self.blob_path, 'rb') as f:
                    self.items = pickle.load(f)
                print(f"Loaded {len(self.items)} items from {self.blob_path}")
            except (pickle.UnpicklingError, EOFError, gzip.BadGzipFile) as e:
                print(f"Warning: Could not load data blob from {self.blob_path}. Starting fresh. Error: {e}")
                self.items = {}
            except Exception as e:
                print(f"An unexpected error occurred while loading: {e}")
                self.items = {}


    def save_store(self):
        """Saves the current hash-to-string dictionary to the compressed blob file."""
        try:
            with gzip.open(self.blob_path, 'wb') as f:
                pickle.dump(self.items, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Successfully saved {len(self.items)} items to {self.blob_path}")
        except IOError as e:
            print(f"Error: Could not write to blob file at {self.blob_path}. Error: {e}")

    def __contains__(self, item_hash: str) -> bool:
        """Allows for `in` operator checking against hashes."""
        return item_hash in self.items

    def __len__(self) -> int:
        """Returns the number of unique items stored."""
        return len(self.items)

class DedupeEngine:
    """
    A deduplication engine that processes text lines and files,
    using hashing to identify and store unique entries.
    """

    def __init__(self, hash_store: HashStore):
        """
         Initializes the DedupeEngine with a specific hash store.

        Args:
            hash_store (HashStore): The storage backend for hashes and strings.
        """
        self.hash_store = hash_store

    @staticmethod
    def _generate_hash(text: str) -> str:
        """
        Generates a 4-byte hash (8 hex characters) for a given text string.

        This is done by truncating the full SHA-256 hash. This is not
        guaranteed to be unique and is susceptible to collisions.

        Args:
            text (str): The input string to hash.

        Returns:
            str: The hexadecimal representation of the 4-byte hash.
        """
        # Normalize the string to ensure consistent hashing
        normalized_text = text.strip().lower()
        # Truncate the full SHA-256 hash to the first 8 characters (4 bytes)
        return hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()[16:]

    def process_line(self, line: str) -> Tuple[Union[str, None], bool]:
        """
        Processes a single line of text to check for duplicates.

        Args:
            line (str): The line of text to process.

        Returns:
            Tuple[Union[str, None], bool]: A tuple containing the original line
                                           if it's unique (or None) and a boolean
                                           indicating if it was a new addition.
        """
        stripped_line = line.strip()
        if not stripped_line:
            return None, False # Ignore empty lines

        line_hash = self._generate_hash(stripped_line)
        # We pass the stripped line to the store to save space and be consistent.
        is_new = self.hash_store.add_item(line_hash, stripped_line)
        
        if is_new:
            # Return the original, un-stripped line to preserve original formatting in output file.
            return line, True
        return None, False

    def process_file(self, input_file_path: str, output_file_path: str):
        """
        Processes an entire file line by line for deduplication and stores hashes.

        This method is memory-efficient as it reads the file line by line
        instead of loading the entire file into memory.

        Args:
            input_file_path (str): Path to the source text file.
            output_file_path (str): Path to write the deduplicated lines.
        """
        new_lines_count = 0
        try:
            # Open the output file in binary mode
            with open(input_file_path, 'r', encoding='utf-8') as infile, \
                 open(output_file_path, 'wb') as outfile:
                for line in infile:
                    stripped_line = line.strip()
                    if not stripped_line:
                        # Write a special binary marker for a blank line
                        outfile.write(b'\x00')
                        continue

                    line_hash = self._generate_hash(stripped_line)
                    # Add the item to the store. is_new will be True if it was a new item.
                    is_new = self.hash_store.add_item(line_hash, stripped_line)
                    
                    if is_new:
                        new_lines_count += 1
                    
                    # Convert the hex hash to binary and write it to the file
                    outfile.write(bytes.fromhex(line_hash))

            print(f"Processed {input_file_path}. Added {new_lines_count} new unique lines to the store.")
            print(f"Hashes of all non-empty content written to {output_file_path} in compact binary format.")
        except FileNotFoundError:
            print(f"Error: Input file not found at {input_file_path}")
        except IOError as e:
            print(f"Error processing file: {e}")

    def save_state(self):
        """Persists the current hash store to its blob file."""
        self.hash_store.save_store()

# --- Command Line Interface Logic ---

def main():
    """
    Main function to parse command-line arguments and run the deduplication tool.
    """
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="A command-line tool for text deduplication using a persistent hash store.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Use a mutually exclusive group to ensure only one main action is specified
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--seed",
        metavar="GLOB_PATTERN",
        type=str,
        help=(
            "Takes a glob of *.txt files (e.g., 'data/*.txt') and uses them to\n"
            "seed the hash table. Saves the hash table to 'dedupe_main.db'."
        )
    )

    group.add_argument(
        "--input",
        metavar="INPUT_FILE",
        type=str,
        help="Specifies the text file to be deduped."
    )

    group.add_argument(
        "--decode",
        metavar="HASH_FILE",
        type=str,
        help=(
            "Takes a file where each line is a hash and prints the original\n"
            "string associated with that hash from the database. Preserves spacing."
        )
    )

    # Arguments that can be used with others
    parser.add_argument(
        "--output",
        metavar="OUTPUT_FILE",
        type=str,
        help=(
            "Specifies the output file for deduplicated content. Required when\n"
            "using --input. Default is 'deduplicated_output.txt'."
        ),
        default="deduplicated_output.txt"
    )

    parser.add_argument(
        "--db",
        metavar="DB_PATH",
        type=str,
        help=(
            "Specifies the path for the hash database. Default is 'dedupe_main.db'."
        ),
        default="dedupe_main.db"
    )

    args = parser.parse_args()

    # Get the database path from the arguments
    db_path = args.db

    # --- Handle the different command-line actions ---

    # Action 1: Seed the database
    if args.seed:
        print(f"Seeding database '{db_path}' with files matching glob pattern: '{args.seed}'")
        file_paths = glob.glob(args.seed, recursive=True)
        if not file_paths:
            print(f"Warning: No files found matching '{args.seed}'. Exiting.")
            sys.exit(1)

        hash_store = HashStore(db_path)
        engine = DedupeEngine(hash_store)
        
        total_new_lines = 0
        total_lines = 0
        
        for file_path in file_paths:
            print(f"Processing file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        total_lines += 1
                        _, is_new = engine.process_line(line)
                        if is_new:
                            total_new_lines += 1
            except FileNotFoundError:
                print(f"Error: File not found at {file_path}. Skipping.")
            except Exception as e:
                print(f"An unexpected error occurred while processing {file_path}: {e}. Skipping.")

        print(f"\n--- Seeding Complete ---")
        print(f"Processed {len(file_paths)} file(s) and {total_lines} total lines.")
        print(f"Added {total_new_lines} new unique lines to the database.")
        engine.save_state()

    # Action 2: Dedupe a single file
    elif args.input:
        if not args.output:
            print("Error: --output is required when using --input.")
            sys.exit(1)
        
        print(f"Deduplicating input file '{args.input}' to output file '{args.output}' using database '{db_path}'")
        
        hash_store = HashStore(db_path)
        engine = DedupeEngine(hash_store)
        
        engine.process_file(args.input, args.output)
        engine.save_state()

    # Action 3: Decode hashes
    elif args.decode:
        print(f"Decoding binary hashes from '{args.decode}' using database '{db_path}'")
        
        hash_store = HashStore(db_path)
        
        try:
            # Open the input file in binary mode
            with open(args.decode, 'rb') as f:
                while True:
                    # Read one byte to check for the blank line marker
                    marker_byte = f.read(1)
                    if not marker_byte:
                        # End of file
                        break
                    
                    if marker_byte == b'\x00':
                        # Found a blank line marker, print a newline
                        print()
                        continue
                    
                    # It's not a marker, so it must be the first byte of a hash
                    hash_bytes = marker_byte + f.read(3)
                    
                    if len(hash_bytes) != 4:
                        print(f"Warning: Unexpected file format. Hash length is not 4 bytes.")
                        break

                    # Convert the binary hash back to a hex string
                    hash_value = hash_bytes.hex()
                    
                    original_string = hash_store.get_string_by_hash(hash_value)
                    if original_string:
                        # Print the original string
                        print(original_string)
                    else:
                        print(f"Warning: Hash '{hash_value}' not found in the database.")
        except FileNotFoundError:
            print(f"Error: Hash file not found at {args.decode}")
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred while decoding: {e}")
            sys.exit(1)

    else:
        # This part should be unreachable due to mutually exclusive group
        parser.print_help()


if __name__ == "__main__":
    main()

