#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN 100000
#define MAX_COLS 400
#define MAX_DIAGS 100
#define MAX_CODES 15000
#define MAX_CODE_LEN 10

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

int cmp_codes(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf_s(stderr, "Usage: %s input.csv [output.csv]\n", argv[0]);
        return 1;
    }
    const char *infilename = argv[1];
    char outfilename[1024];
    if (argc >= 3) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2], sizeof(outfilename)-1);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
    }

    FILE *fout = NULL;
    if (fopen_s(&fout, outfilename, "w") != 0 || !fout) {
        fprintf_s(stderr, "Could not open output file: %s\n", outfilename);
        return 1;
    }

    // First pass: collect unique codes
    FILE *fin = NULL;
    if (fopen_s(&fin, infilename, "r") != 0 || !fin) {
        fprintf_s(stderr, "Could not open input file: %s\n", infilename);
        fclose(fout);
        return 1;
    }
    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0, diag_start = -1, diag_end = -1;
    char *codes[MAX_CODES];
    int code_count = 0;
    int line_count = 0;

    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        fclose(fin);
        fclose(fout);
        return 1;
    }
    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, sizeof(header)-1);
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

    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, sizeof(row)-1);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS);
        for (int i = diag_start; i <= diag_end && i < row_ncols; ++i) {
            char *val = cols[i];
            if (val && val[0]) {
                int found = 0;
                for (int j = 0; j < code_count; ++j) {
                    if (strcmp(codes[j], val) == 0) {
                        found = 1;
                        break;
                    }
                }
                if (!found && code_count < MAX_CODES) {
                    codes[code_count] = _strdup(val);
                    code_count++;
                }
            }
        }
        line_count++;
    }
    fclose(fin);

    // Sort codes alphabetically
    qsort(codes, code_count, sizeof(char*), cmp_codes);

    printf("Found %d unique DIAG codes. Processing %d rows.\n", code_count, line_count);

    // Second pass: one-hot encode
    if (fopen_s(&fin, infilename, "r") != 0 || !fin) {
        fprintf_s(stderr, "Could not open files for second pass.\n");
        if (fin) fclose(fin);
        fclose(fout);
        for (int i = 0; i < code_count; ++i) free(codes[i]);
        return 1;
    }

    // Write header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Unexpected error reading header.\n");
        fclose(fin);
        fclose(fout);
        for (int i = 0; i < code_count; ++i) free(codes[i]);
        return 1;
    }
    line[strcspn(line, "\r\n")] = 0;
    fprintf_s(fout, "%s", line);
    for (int i = 0; i < code_count; ++i) {
        fprintf_s(fout, ",DIAG_%s", codes[i]);
    }
    fprintf_s(fout, "\n");

    // Progress reporting
    int progress = 0, last_progress = -1;
    int row_idx = 0;

    while (fgets(line, sizeof(line), fin)) {
        row_idx++;
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, sizeof(row)-1);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS);
        // Write original columns
        for (int i = 0; i < ncols; ++i) {
            fprintf_s(fout, "%s%s", cols[i], (i < ncols-1) ? "," : "");
        }
        // Build set of present codes for this row
        bool present[MAX_CODES] = {0};
        for (int i = diag_start; i <= diag_end && i < row_ncols; ++i) {
            char *val = cols[i];
            if (val && val[0]) {
                // Binary search since codes[] is sorted
                int lo = 0, hi = code_count-1;
                while (lo <= hi) {
                    int mid = (lo + hi) / 2;
                    int cmp = strcmp(val, codes[mid]);
                    if (cmp == 0) {
                        present[mid] = true;
                        break;
                    } else if (cmp < 0) {
                        hi = mid - 1;
                    } else {
                        lo = mid + 1;
                    }
                }
            }
        }
        // Write one-hot columns
        for (int i = 0; i < code_count; ++i) {
            fprintf_s(fout, ",%d", present[i] ? 1 : 0);
        }
        fprintf_s(fout, "\n");

        // Progress
        progress = (int)((row_idx * 100.0) / line_count + 0.5);
        if (progress != last_progress && progress % 1 == 0) {
            printf("\rProgress: %d%%", progress);
            fflush(stdout);
            last_progress = progress;
        }
    }
    printf("\rProgress: 100%%\n");

    fclose(fin);
    fclose(fout);
    for (int i = 0; i < code_count; ++i) free(codes[i]);
    printf("Done. Output written to %s\n", outfilename);
    return 0;
}