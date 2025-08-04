'''
    This module provides various utilities for translating things from one format to another.
'''
import os


def get_cc_file_for_chapter(chapter: str) -> str:
    '''
        Returns the path to the CC list file for a given HRG chapter.
    '''
    directory = os.path.abspath("./data/cc_codes/individual_lists")
    files = os.listdir(directory)
    chapter_files = [f for f in files if f.startswith(f"{chapter}_") and f.endswith("_cc_list.csv")]
    integers = [int(f.split("_")[1]) for f in chapter_files]
    if not integers:
        raise ValueError(f"No files found for chapter {chapter}")
    highest_int = max(integers)
    return os.path.join(directory, f"{chapter}_{highest_int}_cc_list.csv")


def format_dx_code_to_hrg(code: str) -> str:
    '''
        Converts a standard diagnosis code to HRG format.
    '''
    if '.' in code:
        code = code.replace('.', '')
    if len(code) <= 3:
        code = f"{code}X"
    return code


def format_hrg_dx_code_to_standard(code: str) -> str:
    '''
        Converts an HRG-formatted diagnosis code to standard format.
    '''
    if code.endswith("X"):
        code = code[:-1]
    return f"{code[:3]}.{code[3:]}" if len(code) > 3 else code


def format_px_code_to_hrg(code: str) -> str:
    '''
        Converts a standard procedure code to HRG format.
    '''
    return code.replace('.', '')


def format_hrg_px_code_to_standard(code: str) -> str:
    '''
        Converts an HRG-formatted procedure code to standard format.
    '''
    return f"{code[:3]}.{code[3:]}"
