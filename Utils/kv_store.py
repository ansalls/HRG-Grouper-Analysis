'''
    This module provides functions to save and load a key-value store to and from a JSON file.
'''
from json import dump, load

def save_kv_store(kv_store: dict, output_filename: str, silent=True) -> None:
    '''
    Saves a key-value dictionary to a JSON file.

    Args:
        kv_store (dict): The dictionary to save.
        output_filename (str): The filename (and path) to write the JSON data to.
    '''
    with open(output_filename, 'w', encoding='utf-8') as f:
        dump(kv_store, f, indent=4)
    if not silent:
        print(f"Key-value store saved to {output_filename}")

def load_kv_store(input_filename: str) -> dict:
    '''
    Loads the key-value store from a JSON file.

    Args:
        input_filename (str): The filename (and path) from which to read the JSON data.

    Returns:
        dict: The loaded key-value dictionary.
    '''
    with open(input_filename, 'r', encoding='utf-8') as f:
        kv_store = load(f)
    return kv_store
