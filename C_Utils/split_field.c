// Reads a CSV file, splits a specified column into multiple columns based
// on a delimiter, and writes to a new CSV file.
// Usage: split_field [-n Nth instance or -1 for last] [-c col_delim] [-d split_delim] input.csv [output.csv] col_to_split

#include "csv_utils.h"

#define MAX_DELIM_LEN 16

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
    if (!open_input_output_files(infilename, outfilename, &fin, &fout)) {
        return 1;
    }
    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0;

    // Read header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        close_files(fin, fout);
        return 1;
    }


    line[strcspn(line, "\r\n")] = '\0';

    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, _TRUNCATE);
    header[sizeof(header)-1] = 0;
    ncols = csv_split_line_delim(header, cols, MAX_COLS, col_delim);
    if (col_to_split > ncols) {
        fprintf_s(stderr, "Column to split out of range. File has %d columns.\n", ncols);
        close_files(fin, fout);
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
        int row_ncols = csv_split_line_delim(row, cols, MAX_COLS, col_delim);
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
        csv_write_row_delim(fout, outcols, ncols+1, col_delim);
    }
    close_files(fin, fout);
    return 0;
}