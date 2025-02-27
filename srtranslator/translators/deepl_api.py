import os
import csv
import deepl
import hashlib
from pathlib import Path
from .base import Translator


class DeeplApi(Translator):
    max_char = 1500
    GLOSSARY_NAME = "myllm_glossary"
    GLOSSARY_PATH = "glossary/glossary.csv"
    GLOSSARY_HASH_PATH = "glossary/.glossary_hash"

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("DeepL API key is required. Please set the DEEPL_API_KEY environment variable.")
        
        try:
            self.translator = deepl.Translator(api_key)
            # Test the API key by getting usage information
            self.translator.get_usage()
        except Exception as e:
            print(f"Error initializing DeepL API: {e}")
            print("Please check your API key and make sure your DeepL account is active.")
            raise
            
        self.glossary = None
        self.setup_glossary()

    def get_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def is_glossary_modified(self):
        """Check if glossary file has been modified by comparing hash"""
        if not os.path.exists(self.GLOSSARY_PATH):
            return False

        current_hash = self.get_file_hash(self.GLOSSARY_PATH)
        
        # If hash file doesn't exist, consider glossary as modified
        if not os.path.exists(self.GLOSSARY_HASH_PATH):
            with open(self.GLOSSARY_HASH_PATH, "w", encoding="utf-8") as f:
                f.write(current_hash)
            return True
        
        # Compare current hash with stored hash
        try:
            with open(self.GLOSSARY_HASH_PATH, "r", encoding="utf-8") as f:
                stored_hash = f.read().strip()
        except UnicodeDecodeError:
            # If there's an encoding error, recreate the hash file
            with open(self.GLOSSARY_HASH_PATH, "w", encoding="utf-8") as f:
                f.write(current_hash)
            return True
        
        if current_hash != stored_hash:
            # Update hash file
            with open(self.GLOSSARY_HASH_PATH, "w", encoding="utf-8") as f:
                f.write(current_hash)
            return True
        
        return False

    def read_glossary_entries(self):
        """Read glossary entries from CSV file"""
        entries = {}
        with open(self.GLOSSARY_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    source_term = row[0].strip()
                    target_term = row[1].strip()
                    if source_term and target_term:
                        entries[source_term] = target_term
        return entries

    def create_or_update_glossary(self, source_lang, target_lang):
        """Create or update DeepL glossary"""
        try:
            # Check if glossary already exists
            existing_glossaries = self.translator.list_glossaries()
            for glossary in existing_glossaries:
                if glossary.name == self.GLOSSARY_NAME:
                    # Delete existing glossary
                    self.translator.delete_glossary(glossary)
                    break
            
            # Create new glossary
            entries = self.read_glossary_entries()
            if entries:
                self.glossary = self.translator.create_glossary(
                    self.GLOSSARY_NAME,
                    source_lang,
                    target_lang,
                    entries=entries
                )
                return True
        except Exception as e:
            print(f"Error creating/updating glossary: {e}")
        return False

    def setup_glossary(self):
        """Setup glossary if needed"""
        self.glossary = None
        if os.path.exists(self.GLOSSARY_PATH) and self.is_glossary_modified():
            # We'll create the glossary when translate is called with language info
            pass

    def translate(self, text: str, source_language: str, destination_language: str):
        # Create or update glossary if needed
        if os.path.exists(self.GLOSSARY_PATH) and self.is_glossary_modified():
            self.create_or_update_glossary(source_language, destination_language)
        
        # Use glossary if available
        glossary_id = None
        if self.glossary is None:
            # Try to find existing glossary
            try:
                existing_glossaries = self.translator.list_glossaries()
                for glossary in existing_glossaries:
                    if glossary.name == self.GLOSSARY_NAME:
                        self.glossary = glossary
                        break
            except Exception as e:
                print(f"Error finding existing glossary: {e}")
        
        if self.glossary is not None:
            try:
                result = self.translator.translate_text(
                    text, 
                    source_lang=source_language, 
                    target_lang=destination_language,
                    glossary=self.glossary
                )
                return result.text
            except Exception as e:
                print(f"Error translating with glossary: {e}")
                # Fall back to translation without glossary
        
        # Translate without glossary
        result = self.translator.translate_text(
            text, source_lang=source_language, target_lang=destination_language
        )
        return result.text
