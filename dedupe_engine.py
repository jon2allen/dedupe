import hashlib
import pickle
import gzip
import os
from typing import Set, IO, Union, Tuple, Dict

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

        Args:
            item_hash (str): The hash of the string.
            original_string (str): The original string to store.

        Returns:
            bool: True if the item was new and added, False otherwise.
        """
        if item_hash not in self.items:
            self.items[item_hash] = original_string
            return True
        return False

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
        Generates a SHA-256 hash for a given text string.

        Args:
            text (str): The input string to hash.

        Returns:
            str: The hexadecimal representation of the hash.
        """
        # Normalize the string to ensure consistent hashing
        normalized_text = text.strip().lower()
        return hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()

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
        Processes an entire file line by line for deduplication.

        This method is memory-efficient as it reads the file line by line
        instead of loading the entire file into memory.

        Args:
            input_file_path (str): Path to the source text file.
            output_file_path (str): Path to write the deduplicated lines.
        """
        new_lines_count = 0
        try:
            with open(input_file_path, 'r', encoding='utf-8') as infile, \
                 open(output_file_path, 'w', encoding='utf-8') as outfile:
                for line in infile:
                    unique_line, is_new = self.process_line(line)
                    if is_new and unique_line is not None:
                        outfile.write(unique_line)
                        new_lines_count += 1
            print(f"Processed {input_file_path}. Found {new_lines_count} new unique lines.")
            print(f"Deduplicated content written to {output_file_path}")
        except FileNotFoundError:
            print(f"Error: Input file not found at {input_file_path}")
        except IOError as e:
            print(f"Error processing file: {e}")

    def save_state(self):
        """Persists the current hash store to its blob file."""
        self.hash_store.save_store()


if __name__ == '__main__':
    # --- Example Usage ---

    # 1. Initialize the HashStore and DedupeEngine
    hash_store = HashStore('my_report_store.pkl.gz')
    engine = DedupeEngine(hash_store)

    # 2. Process individual lines
    print("\n--- Processing individual lines ---")
    phrases = [
        "The quick brown fox jumps over the lazy dog.",
        "A stitch in time saves nine.",
        "The quick brown fox jumps over the lazy dog.", # Duplicate
        "To be or not to be, that is the question."
    ]

    for phrase in phrases:
        _, is_new = engine.process_line(phrase)
        status = "Added (New)" if is_new else "Skipped (Duplicate)"
        print(f"'{phrase[:30]}...': {status}")

    print(f"Total unique items after processing lines: {len(engine.hash_store)}")

    # 3. Process a file
    print("\n--- Processing a file ---")
    input_filename = 'sample_report.txt'
    output_filename = 'deduplicated_report.txt'
    with open(input_filename, 'w', encoding='utf-8') as f:
        f.write("This is the first line of the report.\n")
        f.write("This is the second line, which is unique.\n")
        f.write("This is the first line of the report.\n") # Duplicate
        f.write("A final, unique thought.\n")
        f.write("A stitch in time saves nine.\n") # Duplicate from line processing

    engine.process_file(input_filename, output_filename)

    print(f"\nTotal unique items after file processing: {len(engine.hash_store)}")

    # 4. Save the final state
    engine.save_state()

    # 5. --- NEW: Retrieve a string by its hash ---
    print("\n--- Verifying string retrieval by hash ---")
    # Let's get the hash for a known unique phrase
    known_phrase = "A stitch in time saves nine."
    known_hash = DedupeEngine._generate_hash(known_phrase)
    
    print(f"Looking for hash: {known_hash[:10]}...")
    retrieved_string = engine.hash_store.get_string_by_hash(known_hash)
    
    if retrieved_string:
        print(f"Success! Retrieved string: '{retrieved_string}'")
        assert retrieved_string == known_phrase
    else:
        print("Error: Could not retrieve the string.")

    # To clean up the created files:
    # os.remove(input_filename)
    # os.remove(output_filename)
    # os.remove('my_report_store.pkl.gz')

