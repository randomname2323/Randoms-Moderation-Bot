import json
import os
import logging

logger = logging.getLogger(__name__)

data_cache = {}

def setup_data(the_file, start_stuff):
    if not os.path.exists(the_file):
        os.makedirs(os.path.dirname(the_file), exist_ok=True)
        with open(the_file, 'w') as f:
            json.dump(start_stuff, f, indent=4)
        data_cache[the_file] = start_stuff
        logger.info(f"Created {the_file} with default data")

def read_data(the_file):
    if the_file in data_cache:
        return data_cache[the_file]
    
    try:
        if not os.path.exists(the_file):
            return {}
        with open(the_file, 'r') as f:
            data = json.load(f)
            data_cache[the_file] = data
            return data
    except Exception as e:
        logger.error(f"Error loading {the_file}: {e}")
        return {}

def write_data(the_file, data):
    data_cache[the_file] = data
    try:
        os.makedirs(os.path.dirname(the_file), exist_ok=True)
        with open(the_file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving {the_file}: {e}")

word_cache = None

def get_words(the_file):
    global word_cache
    if word_cache is not None:
        return word_cache
        
    try:
        with open(the_file, "r") as f:
            words = [line.strip().lower() for line in f if line.strip()]
            word_cache = words
            return words
    except FileNotFoundError:
        logger.warning(f"{the_file} not found, returning empty list")
        return []
