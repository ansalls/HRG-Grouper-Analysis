// Reads a CSV file, copies lines to a new file if condition is met.
// Usage: drop_if_cols_dif [-n] input.csv [output.csv] col1 col2

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN 100000
#define MAX_COLS 400

int split_line(char *line, char *cols[], int max_cols) {
    int count = 0;
    char *start = line;
    char *p = line;
    while (*p && count < max_cols) {
        if (*p == ',') {
            *p = '\0';
            cols[count++] = start;
            start = p + 1;
        }
        p++;
    }
    cols[count++] = start;
    return count;
}

void write_row(FILE *f, char *cols[], int ncols) {
    for (int i = 0; i < ncols; ++i) {
        fprintf_s(f, "%s%s", cols[i], (i < ncols-1) ? "," : "\n");
    }
}

void make_output_filename(const char *input, char *output, size_t outlen) {
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

int main(int argc, char *argv[]) {
    char outfilename[1024];
    bool not_flag = false;
    int arg_offset = 0;

    // Check for -n flag
    if (argc > 1 && strcmp(argv[1], "-n") == 0) {
        not_flag = true;
        arg_offset = 1;
    }

    if ((argc != 4 + arg_offset) && (argc != 5 + arg_offset)) {
        fprintf_s(stderr, "Usage: %s [-n] input.csv [output.csv] col1 col2\n", argv[0]);
        return 1;
    }
    const char *infilename = argv[1 + arg_offset];
    int col1, col2;
    if (argc == 5 + arg_offset) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2 + arg_offset], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
        col1 = atoi(argv[3 + arg_offset]);
        col2 = atoi(argv[4 + arg_offset]);
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
        col1 = atoi(argv[2 + arg_offset]);
        col2 = atoi(argv[3 + arg_offset]);
    }
    if (col1 < 1 || col2 < 1) {
        fprintf_s(stderr, "Column positions must be >= 1.\n");
        return 1;
    }
    FILE *fin = NULL;
    FILE *fout = NULL;
    if (fopen_s(&fin, infilename, "r") != 0 || fopen_s(&fout, outfilename, "w") != 0) {
        fprintf_s(stderr, "Error opening files.\n");
        return 1;
    }
    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0;

    // Handle header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        fclose(fin);
        fclose(fout);
        return 1;
    }
    fputs(line, fout);

    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, _TRUNCATE);
    header[sizeof(header)-1] = 0;
    ncols = split_line(header, cols, MAX_COLS);
    if (col1 > ncols || col2 > ncols) {
        fprintf_s(stderr, "Column positions out of range. File has %d columns.\n", ncols);
        fclose(fin);
        fclose(fout);
        return 1;
    }
    // Process each row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) continue;
        bool equal = (strcmp(cols[col1-1], cols[col2-1]) == 0);
        if ((!not_flag && equal) || (not_flag && !equal)) {
            fprintf_s(fout, "%s\n", line);
        }
    }
    fclose(fin);
    fclose(fout);
    return 0;
}
