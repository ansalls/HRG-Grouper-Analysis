'''
    This module contains a function that runs a Windows command line
    program and waits for its completion.
'''
import subprocess

def run_command_and_wait(command: list[str], silent=False) -> bool:
    '''
    Runs a Windows command line program and waits for its completion.

    :param command: A list containing the command and its arguments.
    :return: true if command completed successfully, else false.
    '''
    if not silent:
        print(f"Running command: {' '.join(command)}")

    completed_process = subprocess.run(command, capture_output=True, text=True, check=False)

    if not silent:
        if completed_process.returncode == 0:
            print("Success")
        else:
            print(f"Error - command return code: {completed_process.returncode}")

        if completed_process.stdout:
            print(f"Standard Output: {completed_process.stdout}")

        if completed_process.stderr:
            print(f"Standard Error: {completed_process.stderr}")

    return completed_process.returncode == 0
