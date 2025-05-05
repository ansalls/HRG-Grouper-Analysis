// Reads a CSV file, writes only rows where the number of populated DIAG_XX columns
//  for each PROVSPNO root matches the minimum for that root.
// Usage: drop_if_diags_exceed input.csv [output.csv]

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#define MAX_LINE_LEN 100000
#define MAX_COLS 400
#define MAX_PROVSPNO_ROOT 100000
#define MAX_PROVSPNO_LEN 256
#define MAX_DIAGS 99

struct provspno_min {
    char root[MAX_PROVSPNO_LEN];
    int min_count;
};

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

// Helper: Extract PROVSPNO root (before '|')
void get_provspno_root(const char *provspno, char *root, size_t maxlen) {
    const char *pipe = strchr(provspno, '|');
    if (pipe) {
        size_t len = pipe - provspno;
        if (len >= maxlen) len = maxlen - 1;
        strncpy_s(root, maxlen, provspno, len);
        root[len] = '\0';
    } else {
        strncpy_s(root, maxlen, provspno, _TRUNCATE);
    }
}

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
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Program started\n", timestamp);
    int debug = 0;
    int arg_offset = 0;
    if (argc > 1 && strcmp(argv[1], "-d") == 0) {
        debug = 1;
        arg_offset = 1;
    }
    char outfilename[1024];
    if (argc < 2 + arg_offset) {
        fputs("Usage: ", stderr);
        fputs(argv[0], stderr);
        fputs(" [-d] input.csv [output.csv]\n", stderr);
        fputs("[ERROR] Not enough arguments provided.\n", stderr);
        return 1;
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Args parsed.\n", timestamp);
    const char *infilename = argv[1 + arg_offset];
    if (argc >= 3 + arg_offset) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2 + arg_offset], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Input: %s, Output: %s\n", timestamp, infilename, outfilename);
    FILE *fin = NULL;
    FILE *fout = NULL;
    if (fopen_s(&fin, infilename, "r") != 0) {
        get_timestamp(timestamp, sizeof(timestamp));
        fprintf_s(stderr, "[%s] [ERROR] Could not open input file: %s\n", timestamp, infilename);
        return 1;
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Input file opened.\n", timestamp);
    if (fopen_s(&fout, outfilename, "w") != 0) {
        get_timestamp(timestamp, sizeof(timestamp));
        fprintf_s(stderr, "[%s] [ERROR] Could not open output file: %s\n", timestamp, outfilename);
        fclose(fin);
        return 1;
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Output file opened.\n", timestamp);
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
        fclose(fin);
        fclose(fout);
        free(provs);
        return 1;
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Header read.\n", timestamp);

    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, _TRUNCATE);
    header[sizeof(header)-1] = 0;
    memset(cols, 0, sizeof(cols));
    ncols = split_line(header, cols, MAX_COLS);
    for (int i = 0; i < ncols; ++i) {
        if (strncmp(cols[i], "PROVSPNO", 8) == 0) provspno_idx = i;
        if (strncmp(cols[i], "DIAG_01", 8) == 0) diag_start = i;
        if (strncmp(cols[i], "DIAG_", 5) == 0) diag_end = i;
    }
    for (int i = diag_start; i < ncols; ++i) {
        if (cols[i] && strncmp(cols[i], "DIAG_", 5) == 0) diag_end = i;
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Header parsed. ncols=%d, provspno_idx=%d, diag_start=%d, diag_end=%d\n", timestamp, ncols, provspno_idx, diag_start, diag_end);
    if (debug) {
        get_timestamp(timestamp, sizeof(timestamp));
        printf("[%s] [DEBUG] Header columns: %d\n", timestamp, ncols);
        printf("[%s] [DEBUG] PROVSPNO index: %d\n", timestamp, provspno_idx);
        printf("[%s] [DEBUG] DIAG_01 index: %d\n", timestamp, diag_start);
        printf("[%s] [DEBUG] DIAG_XX last index: %d\n", timestamp, diag_end);
    }
    if (provspno_idx < 0) {
        fputs("[ERROR] Could not find PROVSPNO column in header.\n", stderr);
        fclose(fin);
        fclose(fout);
        free(provs);
        return 1;
    }
    if (diag_start < 0) {
        fputs("[ERROR] Could not find DIAG_01 column in header.\n", stderr);
        fclose(fin);
        fclose(fout);
        free(provs);
        return 1;
    }
    if (diag_end < diag_start) {
        fputs("[ERROR] Could not find any DIAG_XX columns in header.\n", stderr);
        fclose(fin);
        fclose(fout);
        free(provs);
        return 1;
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Starting first pass.\n", timestamp);

    // First pass: find min populated DIAG count for each PROVSPNO root
    while (fgets(line, sizeof(line), fin)) {
        total_rows++;
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN] = {0};
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) {
            if (debug) printf("[DEBUG] Skipping malformed row %d (columns: %d)\n", total_rows, row_ncols);
            continue;
        }
        char root[MAX_PROVSPNO_LEN] = {0};
        get_provspno_root(cols[provspno_idx], root, sizeof(root));
        int diag_count = 0;
        for (int i = diag_start; i <= diag_end; ++i) {
            if (cols[i][0] != '\0') diag_count++;
        }
        if (debug) printf("[DEBUG] Row %d: root=%s, diag_count=%d\n", total_rows, root, diag_count);
        find_or_add_root(provs, &nprovs, root, diag_count);
    }
    fclose(fin);
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] First pass complete.\n", timestamp);

    // Second pass: write only rows with min diag count for root
    if (fin) fclose(fin);
    if (fopen_s(&fin, infilename, "r") != 0) {
        fputs("Error reopening input file.\n", stderr);
        fclose(fout);
        free(provs);
        return 1;
    }
    //get_timestamp(timestamp, sizeof(timestamp));
    //printf("[%s] [DEBUG] Second pass started.\n", timestamp);
    if (!fgets(line, sizeof(line), fin)) {
        fclose(fin);
        fclose(fout);
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
        int row_ncols = split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) {
            if (debug) printf("[DEBUG] Skipping malformed row %d (columns: %d)\n", total_rows, row_ncols);
            skipped_rows++;
            continue;
        }
        char root[MAX_PROVSPNO_LEN] = {0};
        get_provspno_root(cols[provspno_idx], root, sizeof(root));
        int diag_count = 0;
        for (int i = diag_start; i <= diag_end; ++i) {
            if (cols[i][0] != '\0') diag_count++;
        }
        int min_count = get_min_for_root(provs, nprovs, root);
        if (debug) printf("[DEBUG] Row %d: root=%s, diag_count=%d, min_count=%d\n", total_rows, root, diag_count, min_count);
        if (diag_count == min_count) {
            write_row(fout, cols, ncols);
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
    fclose(fin);
    fclose(fout);

    return 0;
}
