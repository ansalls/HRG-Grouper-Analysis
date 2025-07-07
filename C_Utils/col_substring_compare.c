// Reads a CSV file, copies lines to a new file only if two specified columns match.
// Usage: col_substring_compare [-n negation] [-i insensitve casing] [-r right-side] [-l length] input.csv [output.csv] col1 col2

#include "csv_utils.h"

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
        return strcasecmp_n(sub1, sub2, cmp_len) == 0;
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
        print_usage_and_exit(argv[0], "[-n] [-i] [-r] [-l length] input.csv [output.csv] col1 col2");
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
    if (!open_input_output_files(infilename, outfilename, &fin, &fout)) {
        return 1;
    }
    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0;

    // Handle header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        close_files(fin, fout);
        return 1;
    }
    fputs(line, fout);
    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, _TRUNCATE);
    header[sizeof(header)-1] = 0;
    ncols = csv_split_line(header, cols, MAX_COLS);
    if (col1 > ncols || col2 > ncols) {
        fprintf_s(stderr, "Column positions out of range. File has %d columns.\n", ncols);
        close_files(fin, fout);
        return 1;
    }
    // Process row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) continue;
        bool equal = substrings_equal(
            cols[col1-1], cols[col2-1],
            cmp_length, right_flag, case_insensitive
        );
        if ((!not_flag && equal) || (not_flag && !equal)) {
            fprintf_s(fout, "%s\n", line);
        }
    }
    close_files(fin, fout);
    return 0;
}
