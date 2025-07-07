#include "csv_utils.h"

// CSV parsing function
int csv_split_line(char *line, char *cols[], int max_cols) {
    return csv_split_line_delim(line, cols, max_cols, ',');
}

// CSV parsing function with configurable delimiter
int csv_split_line_delim(char *line, char *cols[], int max_cols, char delimiter) {
    int count = 0;
    char *start = line;
    char *p = line;
    while (*p && count < max_cols) {
        if (*p == delimiter) {
            *p = '\0';
            cols[count++] = start;
            start = p + 1;
        }
        p++;
    }
    if (count < max_cols) {
        cols[count++] = start;
    }
    return count;
}

// Write a CSV row to file
void csv_write_row(FILE *f, char *cols[], int ncols) {
    csv_write_row_delim(f, cols, ncols, ',');
}

// Write a CSV row to file with configurable delimiter
void csv_write_row_delim(FILE *f, char *cols[], int ncols, char delimiter) {
    for (int i = 0; i < ncols; ++i) {
        fprintf_s(f, "%s%c", cols[i], (i < ncols-1) ? delimiter : '\n');
    }
}

// Generate output filename by adding "_v2" before file extension
void make_output_filename(const char *input, char *output, size_t outlen) {
    // Ensure there is enough space for the new filename, including "_v2" and extension
    size_t input_len = strlen(input);
    size_t min_required = 4 + 1; // "_v2" + null terminator
    if (input_len + min_required > outlen) {
        // Not enough space, set output to empty string and return
        if (outlen > 0) output[0] = '\0';
        return;
    }
    const char *dot = strrchr(input, '.');
    if (!dot || dot == input) {
        snprintf(output, outlen, "%s_v2", input);
    } else {
        size_t base_len = dot - input;
        if (base_len > outlen - 5) base_len = outlen - 5;
        strncpy_s(output, outlen, input, base_len);
        output[base_len] = '\0';
        strncat_s(output, outlen, "_v2", _TRUNCATE);
        strncat_s(output, outlen, dot, _TRUNCATE);
    }
}

// Open input and output files with error handling
bool open_input_output_files(const char *input_file, const char *output_file,
                            FILE **fin, FILE **fout) {
    *fin = NULL;
    *fout = NULL;

    if (fopen_s(fin, input_file, "r") != 0 || !*fin) {
        fprintf_s(stderr, "Could not open input file: %s\n", input_file);
        return false;
    }

    if (fopen_s(fout, output_file, "w") != 0 || !*fout) {
        fprintf_s(stderr, "Could not open output file: %s\n", output_file);
        if (*fin) {
            fclose(*fin);
            *fin = NULL;
        }
        return false;
    }

    return true;
}

// Close files
void close_files(FILE *fin, FILE *fout) {
    if (fin) fclose(fin);
    if (fout) fclose(fout);
}

// Trim whitespace from both ends of a string
void trim_string(char *s) {
    if (!s) return;

    // Trim leading whitespace
    char *start = s;
    while (*start == ' ' || *start == '\t' || *start == '\r' || *start == '\n') {
        start++;
    }

    // Trim trailing whitespace
    char *end = start + strlen(start) - 1;
    while (end > start && (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')) {
        *end-- = '\0';
    }

    // Move trimmed string to beginning if needed
    if (start != s) {
        memmove_s(s, strlen(s) + 1, start, strlen(start) + 1);
    }
}

// Case-insensitive string comparison for n characters
int strcasecmp_n(const char *a, const char *b, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        char ca = a[i], cb = b[i];
        if (ca == 0 || cb == 0) return ca - cb;
        if (tolower((unsigned char)ca) != tolower((unsigned char)cb))
            return (unsigned char)tolower(ca) - (unsigned char)tolower(cb);
    }
    return 0;
}

// Case-insensitive string equality
bool strings_equal_case_insensitive(const char *a, const char *b) {
    if (!a || !b) return a == b;
    return strcasecmp_n(a, b, strlen(a) > strlen(b) ? strlen(a) : strlen(b)) == 0;
}

// Convert string to lowercase in-place
void to_lowercase(char *str) {
    if (!str) return;
    for (int i = 0; str[i]; i++) {
        str[i] = tolower((unsigned char)str[i]);
    }
}

// Compare diagnosis codes (case-insensitive)
bool diag_codes_equal(const char *a, const char *b) {
    if (!a || !b) return a == b;
    return strings_equal_case_insensitive(a, b);
}

// Find diagnosis columns in CSV header
int find_diag_columns(char *cols[], int ncols, int *diag_start, int *diag_end) {
    *diag_start = -1;
    *diag_end = -1;

    for (int i = 0; i < ncols; ++i) {
        if (strncmp(cols[i], "DIAG_01", 7) == 0) {
            *diag_start = i;
        }
        if (strncmp(cols[i], "DIAG_", 5) == 0) {
            *diag_end = i;
        }
    }

    // Ensure we found valid diagnosis columns
    if (*diag_start >= 0 && *diag_end >= *diag_start) {
        return 0; // Success
    }
    return -1; // Error
}

// Find column index by name
int find_column_by_name(char *cols[], int ncols, const char *col_name) {
    for (int i = 0; i < ncols; ++i) {
        if (strcmp(cols[i], col_name) == 0) {
            return i;
        }
    }
    return -1; // Not found
}

// Extract PROVSPNO root (part before the first '|')
void extract_provspno_root(const char *provspno, char *root, size_t maxlen) {
    if (!provspno || !root || maxlen == 0) return;

    const char *pipe = strchr(provspno, '|');
    if (pipe) {
        size_t len = pipe - provspno;
        if (len >= maxlen) len = maxlen - 1;
        strncpy_s(root, maxlen, provspno, len);
        root[len] = '\0';
    } else {
        strncpy_s(root, maxlen, provspno, _TRUNCATE);
    }
}

// Print usage message and exit
void print_usage_and_exit(const char *program_name, const char *usage_string) {
    fprintf_s(stderr, "Usage: %s %s\n", program_name, usage_string);
    exit(1);
}
