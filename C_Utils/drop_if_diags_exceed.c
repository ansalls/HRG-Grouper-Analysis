// Reads a CSV file, writes only rows where the number of populated DIAG_XX columns
//  for each PROVSPNO root matches the minimum for that root.
// Usage: drop_if_diags_exceed input.csv [output.csv]

#include "csv_utils.h"
#include <time.h>

#define MAX_PROVSPNO_ROOT 100000

struct provspno_min {
    char root[MAX_PROVSPNO_LEN];
    int min_count;
};

int find_or_add_root(struct provspno_min *arr, int *n, const char *root, int count) {
    for (int i = 0; i < *n; ++i) {
        if (strcmp(arr[i].root, root) == 0) {
            if (count < arr[i].min_count) arr[i].min_count = count;
            return i;
        }
    }
    if (*n < MAX_PROVSPNO_ROOT) {
        strncpy_s(arr[*n].root, MAX_PROVSPNO_LEN, root, _TRUNCATE);
        arr[*n].min_count = count;
        (*n)++;
        return *n - 1;
    }
    return -1;
}

int get_min_for_root(struct provspno_min *arr, int n, const char *root) {
    for (int i = 0; i < n; ++i) {
        if (strcmp(arr[i].root, root) == 0) return arr[i].min_count;
    }
    return -1;
}

void get_timestamp(char *buf, size_t buflen) {
    time_t now = time(NULL);
    struct tm tstruct;
    localtime_s(&tstruct, &now);
    strftime(buf, buflen, "%Y-%m-%d %H:%M:%S", &tstruct);
}

int main(int argc, char *argv[]) {
    char timestamp[32];
    clock_t start_time = clock();

    int debug = 0;
    int arg_offset = 0;
    if (argc > 1 && strcmp(argv[1], "-d") == 0) {
        debug = 1;
        arg_offset = 1;
    }
    char outfilename[1024];
    if (argc < 2 + arg_offset) {
        print_usage_and_exit(argv[0], "[-d] input.csv [output.csv]");
    }

    const char *infilename = argv[1 + arg_offset];
    if (argc >= 3 + arg_offset) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2 + arg_offset], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
    }

    FILE *fin = NULL;
    FILE *fout = NULL;
    if (!open_input_output_files(infilename, outfilename, &fin, &fout)) {
        return 1;
    }

    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0, provspno_idx = -1, diag_start = -1, diag_end = -1;
    struct provspno_min *provs = malloc(sizeof *provs * MAX_PROVSPNO_ROOT);
    if (!provs) {
        perror("malloc provs");
        return 1;
    }
    int nprovs = 0;
    int total_rows = 0, written_rows = 0, skipped_rows = 0;
    // Handle header
    if (!fgets(line, sizeof(line), fin)) {
        fputs("[ERROR] Empty input file or failed to read header.\n", stderr);
        close_files(fin, fout);
        free(provs);
        return 1;
    }

    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, _TRUNCATE);
    header[sizeof(header)-1] = 0;
    memset(cols, 0, sizeof(cols)); // memset_s is not platform independent
    ncols = csv_split_line(header, cols, MAX_COLS);

    if (find_diag_columns(cols, ncols, &diag_start, &diag_end) != 0) {
        fputs("[ERROR] Could not find DIAG_XX columns in header.\n", stderr);
        close_files(fin, fout);
        free(provs);
        return 1;
    }

    provspno_idx = find_column_by_name(cols, ncols, "PROVSPNO");
    if (provspno_idx < 0) {
        fputs("[ERROR] Could not find PROVSPNO column in header.\n", stderr);
        close_files(fin, fout);
        free(provs);
        return 1;
    }

    // First pass: find min populated DIAG count for each PROVSPNO root
    while (fgets(line, sizeof(line), fin)) {
        total_rows++;
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN] = {0};
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) {
            if (debug) printf("[DEBUG] Skipping malformed row %d (columns: %d)\n",
                total_rows, row_ncols);
            continue;
        }
        char root[MAX_PROVSPNO_LEN] = {0};
        extract_provspno_root(cols[provspno_idx], root, sizeof(root));
        int diag_count = 0;
        for (int i = diag_start; i <= diag_end; ++i) {
            if (cols[i][0] != '\0') diag_count++;
        }
        if (debug) printf("[DEBUG] Row %d: root=%s, diag_count=%d\n", total_rows, root, diag_count);
        find_or_add_root(provs, &nprovs, root, diag_count);
    }
    fclose(fin);

    // Second pass: write only rows with min diag count for root
    if (fin) fclose(fin);
    if (fopen_s(&fin, infilename, "r") != 0) {
        fputs("Error reopening input file.\n", stderr);
        fclose(fout);
        free(provs);
        return 1;
    }

    if (!fgets(line, sizeof(line), fin)) {
        close_files(fin, fout);
        free(provs);
        return 1;
    }
    fputs(line, fout);
    total_rows = 0;

    // Process rows
    while (fgets(line, sizeof(line), fin)) {
        total_rows++;
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN] = {0};
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) {
            if (debug) printf("[DEBUG] Skipping malformed row %d (columns: %d)\n",
                total_rows, row_ncols);
            skipped_rows++;
            continue;
        }
        char root[MAX_PROVSPNO_LEN] = {0};
        extract_provspno_root(cols[provspno_idx], root, sizeof(root));
        int diag_count = 0;
        for (int i = diag_start; i <= diag_end; ++i) {
            if (cols[i][0] != '\0') diag_count++;
        }
        int min_count = get_min_for_root(provs, nprovs, root);
        if (debug) printf("[DEBUG] Row %d: root=%s, diag_count=%d, min_count=%d\n",
            total_rows, root, diag_count, min_count);
        if (diag_count == min_count) {
            csv_write_row(fout, cols, ncols);
            written_rows++;
        } else {
            skipped_rows++;
        }
    }
    free(provs);
    if (debug) {
        get_timestamp(timestamp, sizeof(timestamp));
        double elapsed = (double)(clock() - start_time) / CLOCKS_PER_SEC;
        printf("[%s] [DEBUG] Total rows processed: %d\n", timestamp, total_rows);
        printf("[%s] [DEBUG] Rows written: %d\n", timestamp, written_rows);
        printf("[%s] [DEBUG] Rows skipped: %d\n", timestamp, skipped_rows);
        printf("[%s] [DEBUG] Program finished. Total run time: %.2f seconds\n", timestamp, elapsed);
    }
    close_files(fin, fout);

    return 0;
}
