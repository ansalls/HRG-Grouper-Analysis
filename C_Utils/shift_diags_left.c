// Reads a CSV file, shifts DIAG_XX columns leftward to fill gaps, writes to a new CSV file.
// Usage: shift_diags_left input.csv [output.csv]

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
    if (argc < 2) {
        fprintf_s(stderr, "Usage: %s input.csv [output.csv]\n", argv[0]);
        return 1;
    }
    const char *infilename = argv[1];
    if (argc >= 3) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
    }
    FILE *fin = NULL, *fout = NULL;
    if (fopen_s(&fin, infilename, "r") != 0) {
        fprintf_s(stderr, "Error opening input file: %s\n", infilename);
        perror("fopen_s input");
        return 1;
    }
    if (fopen_s(&fout, outfilename, "w") != 0) {
        fprintf_s(stderr, "Error opening output file: %s\n", outfilename);
        perror("fopen_s output");
        fclose(fin);
        return 1;
    }
    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0, diag_start = -1, diag_end = -1;
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
    for (int i = 0; i < ncols; ++i) {
        if (strncmp(cols[i], "DIAG_01", 8) == 0) diag_start = i;
        if (strncmp(cols[i], "DIAG_", 5) == 0) diag_end = i;
    }
    for (int i = diag_start; i < ncols; ++i) {
        if (cols[i] && strncmp(cols[i], "DIAG_", 5) == 0) diag_end = i;
    }
    if (diag_start < 0 || diag_end < diag_start) {
        fprintf_s(stderr, "Could not find DIAG_XX columns in header.\n");
        fclose(fin);
        fclose(fout);
        return 1;
    }
    // Process row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) {
            for (int i = row_ncols; i < ncols; ++i) cols[i] = "";
        }
        int diag_count = diag_end - diag_start + 1;
        char *shifted[MAX_COLS];
        int s = 0;
        for (int i = diag_start; i <= diag_end; ++i) {
            if (cols[i][0] != '\0') {
                shifted[s++] = cols[i];
            }
        }
        for (int i = s; i < diag_count; ++i) {
            shifted[i] = "";
        }
        for (int i = 0; i < diag_count; ++i) {
            cols[diag_start + i] = shifted[i];
        }
        write_row(fout, cols, ncols);
    }
    fclose(fin);
    fclose(fout);
    return 0;
}