'''
This module sets up the application
'''
import shutil
import os
import datetime
import sys
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv
from tariff_kv_store import get_tariff_kv_store
from Utils.constants import (DATA_FILE_FOLDER,
                             RAW_FILE_FOLDER,
                             SAMPLE_DATA_FILE)

def main():
    '''
    Main function to set up the application
    '''
    # Move the file from ./data/APC_Sample_Test_Data.csv to ./data/raw/
    copy_sample_data_to_raw()

    # Create the KV store for the tariff data
    _ = get_tariff_kv_store()

    # Check if the Grouper executable is available
    if grouper_exe_is_available():
        return # Done

    env_file = ".env"

    # Check if a file path is provided via command line argument
    if len(sys.argv) > 1:
        exe_path = sys.argv[1]
        # Validate the provided path
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"File not found: {exe_path}")
        if not exe_path.lower().endswith('.exe'):
            raise ValueError(f"Error: The provided path is not an .exe file: {exe_path}")
    else:
        # Calculate FYE_TAG for the install dir based on the current year
        # note this is a different format than the tag for national tariffs
        fye_tag = get_current_year_fye_tag()
        suspected_path = (f"C:/Program Files/NHS England/HRG4+ {fye_tag} "
                          "Payment Grouper/HRGGrouperc.exe")
        if os.path.exists(suspected_path):
            exe_path = suspected_path
        else:
            # Open a file explorer dialog with a hint
            root = tk.Tk()
            root.withdraw()  # Hide the main tkinter window

            hint = ("Please select the HRGGrouperc.exe file. It may be "
                    f"located in a path similar to {suspected_path}")
            print(hint)
            exe_path = filedialog.askopenfilename(
                title="Select HRGGrouperc.exe",
                filetypes=[("Executable files", "*.exe")]
                )
            if not exe_path:  # User canceled the dialog
                raise FileNotFoundError("HRGGrouperc.exe not found")

    # Save the file path to .env file
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f'GROUPER_EXE="{exe_path}"\n')

def copy_sample_data_to_raw():
    '''
    Copy sample data to the unmanaged raw directory
    '''
    file_name = SAMPLE_DATA_FILE
    file_dir = DATA_FILE_FOLDER
    source_file = os.path.join(file_dir, file_name)
    destination_dir = RAW_FILE_FOLDER
    destination_file = os.path.join(destination_dir, file_name)

    #Skip if we've already moved the file
    if os.path.exists(destination_file):
        return

    if not os.path.exists(source_file):
        raise FileNotFoundError(f"File not found: {source_file}")

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    shutil.copy(source_file, destination_file)

def get_current_year_fye_tag() -> str:
    '''
    Calculate the current financial year end tag
    '''
    current_year = datetime.datetime.now().year
    next_year = current_year + 1
    last_two = str(next_year)[-2:]
    fye_tag = f"{current_year}_{last_two}"
    return fye_tag

def grouper_exe_is_available() -> bool:
    '''
    Check if the Grouper executable is available
    '''
    load_dotenv()
    if os.getenv("GROUPER_EXE") is not None:
        return True
    return False

if __name__ == "__main__":
    main()
