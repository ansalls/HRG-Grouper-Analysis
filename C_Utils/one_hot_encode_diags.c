#include "csv_utils.h"

#define MAX_CODES 15000
#define MAX_CODE_LEN 10

int cmp_codes(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        print_usage_and_exit(argv[0], "input.csv [output.csv]");
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
    char *cols[MAX_COLS] = {NULL};
    int ncols = 0, diag_start = -1, diag_end = -1;
    char *codes[MAX_CODES];
    int code_count = 0;
    int line_count = 0;

    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        close_files(fin, fout);
        return 1;
    }
    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, sizeof(header)-1);
    header[sizeof(header)-1] = 0;
    ncols = csv_split_line(header, cols, MAX_COLS);
    for (int i = 0; i < ncols; ++i) {
        if (strncmp(cols[i], "DIAG_01", 8) == 0) diag_start = i;
        if (strncmp(cols[i], "DIAG_", 5) == 0) diag_end = i;
    }
    for (int i = diag_start; i < ncols; ++i) {
        if (cols[i] && strncmp(cols[i], "DIAG_", 5) == 0) diag_end = i;
    }
    if (diag_start < 0 || diag_end < diag_start) {
        fprintf_s(stderr, "Could not find DIAG_XX columns in header.\n");
        close_files(fin, fout);
        return 1;
    }

    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, sizeof(row)-1);
        row[sizeof(row)-1] = 0;
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
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
        close_files(fin, fout);
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
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
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

    close_files(fin, fout);
    for (int i = 0; i < code_count; ++i) free(codes[i]);
    printf("Done. Output written to %s\n", outfilename);
    return 0;
}