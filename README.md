# HRG-Grouper-Analysis

 Materials used for probing the NHS' HRG grouper software to better understand its behavior

## C_Utils

This directory contains utility programs for processing CSV files in the HRG Grouper Analysis project.

Example of how to compile and run a utility:

```bash
# Compile the utility
clang -Wall -Wextra -Werror -g -O0  csv_utils.c append_diag.c -o append_diag.exe

# Run the utility with input and output files
./append_diag.exe input.csv output.csv
```
