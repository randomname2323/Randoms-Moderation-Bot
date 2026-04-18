import json
import os
import logging

logger = logging.getLogger(__name__)

_cache = {}

def init_json_file(file_path, default_data):
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(default_data, f, indent=4)
        _cache[file_path] = default_data
        logger.info(f"Created {file_path} with default data")

def load_json(file_path):
    if file_path in _cache:
        return _cache[file_path]
    
    try:
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r') as f:
            data = json.load(f)
            _cache[file_path] = data
            return data
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return {}

def save_json(file_path, data):
    _cache[file_path] = data
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving {file_path}: {e}")

_bad_words_cache = None

def load_bad_words(file_path):
    global _bad_words_cache
    if _bad_words_cache is not None:
        return _bad_words_cache
        
    try:
        with open(file_path, "r") as f:
            words = [line.strip().lower() for line in f if line.strip()]
            _bad_words_cache = words
            return words
    except FileNotFoundError:
        logger.warning(f"{file_path} not found, returning empty list")
        return []
