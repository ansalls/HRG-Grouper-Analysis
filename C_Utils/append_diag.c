// For each row in the data file, appends each diagnosis from the diagnosis file
//  (if not already present) to the first empty DIAG_XX column, updates
//  PROVSPNO with the appended value (for tracking), and writes all rows to output.
// Usage: append_diag diag_list.txt data.csv [output.csv]

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LINE_LEN 100000
#define MAX_COLS 400
#define MAX_DIAGS 99
#define MAX_DIAG_LEN 64
#define MAX_PROVSPNO_LEN 256
#define MAX_DIAG_LIST 10000

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

void trim(char *s) {
    char *end;
    while (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n') s++;
    end = s + strlen(s) - 1;
    while (end > s && (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')) *end-- = 0;
}

int diag_eq(const char *a, const char *b) {
    while (*a && *b) {
        if (tolower(*a) != tolower(*b)) return 0;
        a++; b++;
    }
    return *a == *b;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf_s(stderr, "Usage: %s diag_list.txt data.csv [output.csv]\n", argv[0]);
        return 1;
    }
    const char *diaglistfile = argv[1];
    const char *datafile = argv[2];
    char outfilename[1024];
    if (argc >= 4) {
        strncpy_s(outfilename, sizeof(outfilename), argv[3], sizeof(outfilename)-1);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        make_output_filename(datafile, outfilename, sizeof(outfilename));
    }

    char diag_list[MAX_DIAG_LIST][MAX_DIAG_LEN];
    int diag_list_count = 0;
    FILE *fdiag = NULL;
    if (fopen_s(&fdiag, diaglistfile, "r") != 0 || !fdiag) {
        fprintf_s(stderr, "Could not open diagnosis list file: %s\n", diaglistfile);
        return 1;
    }
    char dline[MAX_DIAG_LEN];
    while (fgets(dline, sizeof(dline), fdiag)) {
        trim(dline);
        if (dline[0] == 0) continue;
        strncpy_s(diag_list[diag_list_count], MAX_DIAG_LEN, dline, MAX_DIAG_LEN-1);
        diag_list[diag_list_count][MAX_DIAG_LEN-1] = 0;
        diag_list_count++;
        if (diag_list_count >= MAX_DIAG_LIST) break;
    }
    fclose(fdiag);

    FILE *fin = NULL;
    FILE *fout = NULL;
    if (fopen_s(&fin, datafile, "r") != 0 || !fin) {
        fprintf_s(stderr, "Could not open data file: %s\n", datafile);
        return 1;
    }
    if (fopen_s(&fout, outfilename, "w") != 0 || !fout) {
        fprintf_s(stderr, "Could not open output file: %s\n", outfilename);
        if (fin) fclose(fin);
        return 1;
    }

    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0, diag_start = -1, diag_end = -1, provspno_idx = -1;

    // Handle header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        fclose(fin); fclose(fout);
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
        if (strncmp(cols[i], "PROVSPNO", 8) == 0) provspno_idx = i;
    }
    for (int i = diag_start; i < ncols; ++i) {
        if (cols[i] && strncmp(cols[i], "DIAG_", 5) == 0) diag_end = i;
    }
    if (diag_start < 0 || diag_end < diag_start || provspno_idx < 0) {
        fprintf_s(stderr, "Could not find DIAG_XX or PROVSPNO columns in header.\n");
        fclose(fin); fclose(fout);
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
        write_row(fout, cols, ncols);

        // Add new new diagnosis to the list
        for (int d = 0; d < diag_list_count; ++d) {
            bool found = false;
            for (int i = diag_start; i <= diag_end; ++i) {
                if (cols[i][0] && diag_eq(cols[i], diag_list[d])) {
                    found = true;
                    break;
                }
            }
            if (found) continue;
            int empty_idx = -1;
            for (int i = diag_start; i <= diag_end; ++i) {
                if (cols[i][0] == 0) {
                    empty_idx = i;
                    break;
                }
            }
            if (empty_idx < 0) continue;
            char *new_cols[MAX_COLS];
            for (int i = 0; i < ncols; ++i) new_cols[i] = cols[i];
            new_cols[empty_idx] = diag_list[d];
            static char provspno_buf[MAX_PROVSPNO_LEN*2];
            snprintf(provspno_buf, sizeof(provspno_buf), "%s|%s", cols[provspno_idx], diag_list[d]);
            new_cols[provspno_idx] = provspno_buf;
            write_row(fout, new_cols, ncols);
        }
    }
    fclose(fin);
    fclose(fout);
    return 0;
}
