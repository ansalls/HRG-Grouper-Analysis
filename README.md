# HRG-Grouper-Analysis

 Materials used to probe the NHS's HRG grouper software and better understand its behavior.

## C_Utils

This directory contains utility programs for processing CSV files in the HRG Grouper Analysis project.

Example of how to manually compile and run a utility:

```bash
# Compile the utility
clang -Wall -Wextra -Werror -g -O0  csv_utils.c append_diag.c -o append_diag.exe

# Run the utility with input and output files
./append_diag.exe input.csv output.csv
```

## External dependencies

The project uses the following external dependencies:

- 'clang' or an alternative for compiling C utilities
- 'Python' for running Python scripts
- 'PowerShell' for running PowerShell scripts
- 'NHS Local Payment Grouper' for determining the HRGs assigned (<https://digital.nhs.uk/services/national-casemix-office/downloads-groupers-and-tools/payment-groupers>)
