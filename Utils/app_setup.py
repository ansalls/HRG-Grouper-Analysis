'''
    This module sets up the application
'''
import shutil
import os
import datetime
import sys
import zipfile
import tkinter as tk
from tkinter import filedialog
import requests
from dotenv import load_dotenv
from tariff_kv_store import get_tariff_kv_store
from Utils.constants import (DATA_FILE_FOLDER,
                             RAW_FILE_FOLDER,
                             SAMPLE_DATA_FILE)


def setup():
    '''
        Main function to set up the application
    '''
    # Move the file from ./data/APC_Sample_Test_Data.csv to ./data/raw/
    get_sample_data_to_raw()

    # Create the KV store for the tariff data
    _ = get_tariff_kv_store()

    # Check if the Grouper executable is available
    if grouper_exe_is_available():
        return  # Done

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


def get_sample_data_to_raw():
    '''
        Copy sample data to the unmanaged raw directory
    '''

    url = (
        'https://digital.nhs.uk/binaries/content/assets/website-assets/services/'
        'national-casemix-office/hrg4-2024-25-local-payment-grouper/'
        'hrg4-202425-local-payment-grouper-test-data-and-expected-results-v1.0.zip'
    )
    zip_path = os.path.join(DATA_FILE_FOLDER, 'test_data.zip')
    target_file_path_and_name = (
        'HRG4+ 202425 Local Payment Grouper Test Data and Expected Results v1.0/'
        'APC/HRG4+ 202425 Local Payment Grouper Admitted Patient Care Sample Test Data.csv'
    )

    # Download the file
    response = requests.get(url, stream=True, timeout=15)
    response.raise_for_status()
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    with zipfile.ZipFile(zip_path, 'r') as f:
        f.extract(target_file_path_and_name, path=DATA_FILE_FOLDER)

    shutil.move(
        os.path.join(DATA_FILE_FOLDER, target_file_path_and_name),
        os.path.join(RAW_FILE_FOLDER, SAMPLE_DATA_FILE)
    )

    os.remove(zip_path)

    directory_to_remove = os.path.join(
        DATA_FILE_FOLDER, target_file_path_and_name.split('/', maxsplit=1)[0])
    shutil.rmtree(directory_to_remove)


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
    setup()
