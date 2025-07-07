// Reads a CSV file, shifts DIAG_XX columns leftward to fill gaps, writes to a new CSV file.
// Usage: shift_diags_left input.csv [output.csv]

#include "csv_utils.h"

int main(int argc, char *argv[]) {
    char outfilename[1024];
    if (argc < 2) {
        print_usage_and_exit(argv[0], "input.csv [output.csv]");
    }
    const char *infilename = argv[1];
    if (argc >= 3) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
    }
    FILE *fin = NULL, *fout = NULL;
    if (!open_input_output_files(infilename, outfilename, &fin, &fout)) {
        return 1;
    }
    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS] = {NULL};
    int ncols = 0, diag_start = -1, diag_end = -1;
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

    if (find_diag_columns(cols, ncols, &diag_start, &diag_end) != 0) {
        fprintf_s(stderr, "Could not find DIAG_XX columns in header.\n");
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
        csv_write_row(fout, cols, ncols);
    }
    close_files(fin, fout);
    return 0;
}