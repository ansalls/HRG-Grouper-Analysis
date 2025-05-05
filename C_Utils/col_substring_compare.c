// Reads a CSV file, copies lines to a new file only if two specified columns match.
// Usage: col_substring_compare [-n negation] [-i insensitve casing] [-r right-side] [-l length] input.csv [output.csv] col1 col2

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

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

// I know I've done one of these before. Consider replacing it with this one.
int strncmp_case(const char *a, const char *b, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        char ca = a[i], cb = b[i];
        if (ca == 0 || cb == 0) return ca - cb;
        if (tolower((unsigned char)ca) != tolower((unsigned char)cb))
            return (unsigned char)tolower(ca) - (unsigned char)tolower(cb);
    }
    return 0;
}

bool substrings_equal(const char *s1, const char *s2, int len, bool right, bool case_insensitive) {
    int l1 = (int)strlen(s1), l2 = (int)strlen(s2);
    int cmp_len = len;
    if (len < 0 || len > l1) cmp_len = l1;
    if (len < 0 || len > l2) cmp_len = l2;
    if (cmp_len > l1) cmp_len = l1;
    if (cmp_len > l2) cmp_len = l2;
    const char *sub1 = right ? s1 + l1 - cmp_len : s1;
    const char *sub2 = right ? s2 + l2 - cmp_len : s2;
    if (case_insensitive)
        return strncmp_case(sub1, sub2, cmp_len) == 0;
    else
        return strncmp(sub1, sub2, cmp_len) == 0;
}

int main(int argc, char *argv[]) {
    char outfilename[1024];
    bool not_flag = false;
    bool right_flag = false;
    bool case_insensitive = false;
    int cmp_length = -1; // compare all by default
    int arg_offset = 0;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-n") == 0) {
            not_flag = true;
            arg_offset++;
        } else if (strcmp(argv[i], "-r") == 0) {
            right_flag = true;
            arg_offset++;
        } else if (strcmp(argv[i], "-i") == 0) {
            case_insensitive = true;
            arg_offset++;
        } else if (strcmp(argv[i], "-l") == 0 && i + 1 < argc) {
            cmp_length = atoi(argv[i + 1]);
            arg_offset += 2;
            i++;
        } else {
            break;
        }
    }

    if ((argc != 4 + arg_offset) && (argc != 5 + arg_offset)) {
        fprintf_s(stderr, "Usage: %s [-n] [-i] [-r] [-l length] input.csv [output.csv] col1 col2\n", argv[0]);
        return 1;
    }
    const char *infilename = argv[arg_offset + 1];
    int col1, col2;
    if (argc == 5 + arg_offset) {
        strncpy_s(outfilename, sizeof(outfilename), argv[arg_offset + 2], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
        col1 = atoi(argv[arg_offset + 3]);
        col2 = atoi(argv[arg_offset + 4]);
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
        col1 = atoi(argv[arg_offset + 2]);
        col2 = atoi(argv[arg_offset + 3]);
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
    // Process row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) continue;
        bool equal = substrings_equal(
            cols[col1-1], cols[col2-1],
            cmp_length, right_flag, case_insensitive
        );
        if ((!not_flag && equal) || (not_flag && !equal)) {
            fprintf_s(fout, "%s\n", line);
        }
    }
    fclose(fin);
    fclose(fout);
    return 0;
}
