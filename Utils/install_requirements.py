'''
    Utility script to install dependencies from requirements.txt
'''
import subprocess
import os
import sys


def install_requirements():
    '''
        Install dependencies from requirements.txt
    '''
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    else:
        print(f"{requirements_file} not found. Skipping dependency installation.")
