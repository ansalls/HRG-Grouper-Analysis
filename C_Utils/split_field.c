// Reads a CSV file, splits a specified column into multiple columns based
// on a delimiter, and writes to a new CSV file.
// Usage: split_field [-n Nth instance or -1 for last] [-c col_delim] [-d split_delim] input.csv [output.csv] col_to_split

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LINE_LEN 100000
#define MAX_COLS 400
#define MAX_DELIM_LEN 16

// Mind this has a different signature than other implementations as it
//  needs to support a configurable delimiter for splitting the fields
int split_line(char *line, char *cols[], int max_cols, char col_delim) {
    int count = 0;
    char *start = line;
    char *p = line;
    while (*p && count < max_cols) {
        if (*p == col_delim) {
            *p = '\0';
            cols[count++] = start;
            start = p + 1;
        }
        p++;
    }
    cols[count++] = start;
    return count;
}

void write_row(FILE *f, char *cols[], int ncols, char col_delim) {
    for (int i = 0; i < ncols; ++i) {
        fprintf_s(f, "%s%c", cols[i], (i < ncols-1) ? col_delim : '\n');
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

// Find the pointer to the nth (1-based, or -1 for last) occurrence of delim in str
char *find_nth_delim(const char *str, char delim, int n) {
    if (n == -1) {
        // Last occurrence
        return strrchr(str, delim);
    }
    int count = 0;
    const char *p = str;
    while (*p) {
        if (*p == delim) {
            count++;
            if (count == n) return (char*)p;
        }
        p++;
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    char outfilename[1024];
    int col_to_split = -1;
    char col_delim = ',';
    char split_delim = '|';
    int split_n = 1; // first occurrence
    int argi = 1;

    while (argi < argc) {
        if (strcmp(argv[argi], "-n") == 0 && argi+1 < argc) {
            split_n = atoi(argv[argi+1]);
            argi += 2;
        } else if (strcmp(argv[argi], "-c") == 0 && argi+1 < argc) {
            col_delim = argv[argi+1][0];
            argi += 2;
        } else if (strcmp(argv[argi], "-d") == 0 && argi+1 < argc) {
            split_delim = argv[argi+1][0];
            argi += 2;
        } else {
            break;
        }
    }
    if (argc - argi < 2 || argc - argi > 3) {
        fprintf_s(stderr, "Usage: %s [-n N] [-c col_delim] [-d split_delim] input.csv [output.csv] col_to_split\n", argv[0]);
        fprintf_s(stderr, "  -n N           Split at Nth occurrence (1=first, -1=last, N=exact Nth)\n");
        fprintf_s(stderr, "  -c col_delim   Column delimiter (default: ,)\n");
        fprintf_s(stderr, "  -d split_delim Field split delimiter (default: |)\n");
        return 1;
    }
    const char *infilename = argv[argi];
    if (argc - argi == 3) {
        strncpy_s(outfilename, sizeof(outfilename), argv[argi+1], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
        col_to_split = atoi(argv[argi+2]);
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
        col_to_split = atoi(argv[argi+1]);
    }
    if (col_to_split < 1) {
        fprintf_s(stderr, "Column to split must be >= 1.\n");
        return 1;
    }

    FILE *fin = NULL, *fout = NULL;
    if (fopen_s(&fin, infilename, "r") != 0 || fopen_s(&fout, outfilename, "w") != 0) {
        fprintf_s(stderr, "Error opening files.\n");
        return 1;
    }
    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0;

    // Read header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        fclose(fin);
        fclose(fout);
        return 1;
    }
    // Not sure why this is needed here but not in other programs. Did I do something
    // different in the other programs? Or is it just a quirk of this specific input file?
    line[strcspn(line, "\r\n")] = '\0';

    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, _TRUNCATE);
    header[sizeof(header)-1] = 0;
    ncols = split_line(header, cols, MAX_COLS, col_delim);
    if (col_to_split > ncols) {
        fprintf_s(stderr, "Column to split out of range. File has %d columns.\n", ncols);
        fclose(fin);
        fclose(fout);
        return 1;
    }
    // Write updated header - insert new column after col_to_split
    for (int i = 0; i < ncols; ++i) {
        fprintf_s(fout, "%s", cols[i]);
        if (i == col_to_split-1) {
            fprintf_s(fout, "%cSPLIT_%s", col_delim, cols[i]);
        }
        if (i < ncols-1) {
            fprintf_s(fout, "%c", col_delim);
        }
    }
    fprintf_s(fout, "\n");

    // Process row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS, col_delim);
        if (row_ncols < ncols) {
            for (int i = row_ncols; i < ncols; ++i) cols[i] = "";
        }
        char *outcols[MAX_COLS+1];
        int outidx = 0;
        for (int i = 0; i < ncols; ++i) {
            if (i == col_to_split-1) {
                char *field = cols[i];
                char *split_ptr = find_nth_delim(field, split_delim, split_n);
                static char left[MAX_LINE_LEN], right[MAX_LINE_LEN];
                if (split_ptr) {
                    size_t left_len = split_ptr - field;
                    strncpy_s(left, sizeof(left), field, left_len);
                    left[left_len] = 0;
                    strncpy_s(right, sizeof(right), split_ptr+1, sizeof(right)-1);
                    right[sizeof(right)-1] = 0;
                } else {
                    strncpy_s(left, sizeof(left), field, sizeof(left)-1);
                    left[sizeof(left)-1] = 0;
                    right[0] = 0;
                }
                outcols[outidx++] = left;
                outcols[outidx++] = right;
            } else {
                outcols[outidx++] = cols[i];
            }
        }
        write_row(fout, outcols, ncols+1, col_delim);
    }
    fclose(fin);
    fclose(fout);
    //printf("Inserted new column at position: %d\n", col_to_split + 1);
    return 0;
}
