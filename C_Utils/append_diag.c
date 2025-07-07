// For each row in the data file, appends each diagnosis from the diagnosis file
//  (if not already present) to the first empty DIAG_XX column, updates
//  PROVSPNO with the appended value (for tracking), and writes all rows to output.
// Usage: append_diag diag_list.txt data.csv [output.csv]

#include "csv_utils.h"

#define MAX_DIAG_LIST 10000

int main(int argc, char *argv[]) {
    if (argc < 3) {
        print_usage_and_exit(argv[0], "diag_list.txt data.csv [output.csv]");
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
        trim_string(dline);
        if (dline[0] == 0) continue;
        strncpy_s(diag_list[diag_list_count], MAX_DIAG_LEN, dline, MAX_DIAG_LEN-1);
        diag_list[diag_list_count][MAX_DIAG_LEN-1] = 0;
        diag_list_count++;
        if (diag_list_count >= MAX_DIAG_LIST) break;
    }
    fclose(fdiag);

    FILE *fin = NULL;
    FILE *fout = NULL;
    if (!open_input_output_files(datafile, outfilename, &fin, &fout)) {
        return 1;
    }

    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS] = {NULL};
    int ncols = 0, diag_start = -1, diag_end = -1, provspno_idx = -1;

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

    provspno_idx = find_column_by_name(cols, ncols, "PROVSPNO");
    if (provspno_idx < 0) {
        fprintf_s(stderr, "Could not find PROVSPNO column in header.\n");
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
        csv_write_row(fout, cols, ncols);

        // Add new new diagnosis to the list
        for (int d = 0; d < diag_list_count; ++d) {
            bool found = false;
            for (int i = diag_start; i <= diag_end; ++i) {
                if (cols[i][0] && diag_codes_equal(cols[i], diag_list[d])) {
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
            // snprintf_s is not platform independent
            snprintf(provspno_buf, sizeof(provspno_buf), "%s|%s", cols[provspno_idx], diag_list[d]);
            new_cols[provspno_idx] = provspno_buf;
            csv_write_row(fout, new_cols, ncols);
        }
    }
    close_files(fin, fout);
    return 0;
}
