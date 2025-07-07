// Reads a CSV file, copies lines to a new file if condition is met.
// Usage: drop_if_cols_dif [-n] input.csv [output.csv] col1 col2

#include "csv_utils.h"

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
        print_usage_and_exit(argv[0], "[-n] input.csv [output.csv] col1 col2");
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
    // Process each row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) continue;
        bool equal = (strcmp(cols[col1-1], cols[col2-1]) == 0);
        if ((!not_flag && equal) || (not_flag && !equal)) {
            fprintf_s(fout, "%s\n", line);
        }
    }
    close_files(fin, fout);
    return 0;
}
