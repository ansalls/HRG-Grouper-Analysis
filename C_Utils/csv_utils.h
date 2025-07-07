#ifndef CSV_UTILS_H
#define CSV_UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

// Common constants
#define MAX_LINE_LEN 100000
#define MAX_COLS 400
#define MAX_DIAGS 99
#define MAX_DIAG_LEN 64
#define MAX_PROVSPNO_LEN 256
#define MAX_VAL_LEN 1024

// General file utilities
void make_output_filename(const char *input, char *output, size_t outlen);
bool open_input_output_files(const char *input_file, const char *output_file,
                            FILE **fin, FILE **fout);
void close_files(FILE *fin, FILE *fout);


// CSV parsing and output
int csv_split_line(char *line, char *cols[], int max_cols);
int csv_split_line_delim(char *line, char *cols[], int max_cols, char delimiter);
void csv_write_row(FILE *f, char *cols[], int ncols);
void csv_write_row_delim(FILE *f, char *cols[], int ncols, char delimiter);
int find_column_by_name(char *cols[], int ncols, const char *col_name);

// Error handling
void print_usage_and_exit(const char *program_name, const char *usage_string);

// String utilities
void trim_string(char *s);
int strcasecmp_n(const char *a, const char *b, size_t n);
bool strings_equal_case_insensitive(const char *a, const char *b);
void to_lowercase(char *str);

// Diagnosis utilities
bool diag_codes_equal(const char *a, const char *b);
int find_diag_columns(char *cols[], int ncols, int *diag_start, int *diag_end);

// PROVSPNO utilities
void extract_provspno_root(const char *provspno, char *root, size_t maxlen);

#endif // CSV_UTILS_H
