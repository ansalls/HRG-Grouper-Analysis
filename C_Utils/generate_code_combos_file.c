// Reads a CSV file, generates all non-empty combinations of DIAG_* columns (keeping DIAG_01),
// updates PROVSPNO with |Combination|#combo_ID#, and writes to a new CSV file.
// Usage: generate_code_combos_file input.csv [output.csv]

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN 10000
#define MAX_COLS 400
#define MAX_DIAGS 66
#define MAX_ROWS 1000000
#define PROVSPNO_MAX 256
#define MAX_COMBO_DIAGS 20  // Speaking from experience... ombinitorial explosions are bad, mmkay?

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

void safe_strcpy(char *dest, const char *src, size_t n) {
    strncpy_s(dest, n, src, _TRUNCATE);
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

// Something like a billion times faster than my python implementation, thank goodness!
void generate_combinations(FILE *out, char *orig_cols[], int ncols, int provspno_idx, int combo_start, int sec_diag_indices[], int nsec) {
    int ncombos = 0;
    char *comb_cols[MAX_COLS];
    unsigned int max_mask = (1U << nsec);
    for (unsigned int mask = 0; mask < max_mask; ++mask) {
        for (int i = 0; i < ncols; ++i) comb_cols[i] = orig_cols[i];
        // Blank out DIAG_02..DIAG_N except those in the current mask
        for (int j = 0; j < nsec; ++j) {
            if ((mask & (1U << j)) == 0) {
                comb_cols[sec_diag_indices[j]] = "";
            }
        }
        static char provspno_buf[PROVSPNO_MAX];
        snprintf(provspno_buf, PROVSPNO_MAX, "%s|Combination|%d", orig_cols[provspno_idx], combo_start + ncombos + 1);
        comb_cols[provspno_idx] = provspno_buf;
        write_row(out, comb_cols, ncols);
        ncombos++;
    }
}

int main(int argc, char *argv[]) {
    char outfilename[1024];
    if (argc < 2) {
        fprintf_s(stderr, "Usage: %s input.csv [output.csv]\n", argv[0]);
        return 1;
    }
    const char *infilename = argv[1];
    if (argc >= 3) {
        safe_strcpy(outfilename, argv[2], sizeof(outfilename));
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
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
    int diag_start = -1, ndiags = 0, provspno_idx = -1;
    int combo_counter = 0;

    // Handle header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        return 1;
    }
    fputs(line, fout);

    char header[MAX_LINE_LEN];
    safe_strcpy(header, line, sizeof(header));
    ncols = split_line(header, cols, MAX_COLS);
    for (int i = 0; i < ncols; ++i) {
        if (strncmp(cols[i], "DIAG_01", 8) == 0) diag_start = i;
        if (strncmp(cols[i], "PROVSPNO", 8) == 0) provspno_idx = i;
    }
    for (int i = diag_start; i < ncols; ++i) {
        if (strncmp(cols[i], "DIAG_", 5) == 0) ndiags++;
        else break;
    }
    if (diag_start < 0 || ndiags < 1 || provspno_idx < 0) {
        fprintf_s(stderr, "Could not find required columns.\n");
        return 1;
    }
    // Process row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        safe_strcpy(row, line, sizeof(row));
        int row_ncols = split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) {
            for (int i = row_ncols; i < ncols; ++i) cols[i] = "";
            row_ncols = ncols;
        }
        if (row_ncols != ncols) continue;
        write_row(fout, cols, ncols);
        int nsec = 0;
        int total_sec = 0;
        int sec_diag_indices[MAX_COLS];
        for (int i = 1; i < ndiags; ++i) {
            if (cols[diag_start + i][0] != '\0') {
                if (nsec < MAX_COMBO_DIAGS) {
                    sec_diag_indices[nsec++] = diag_start + i;
                }
                total_sec++;
            }
        }
        if (total_sec > MAX_COMBO_DIAGS) {
            printf("Skipping line (too many diagnoses to swap, max %d): %s\n", MAX_COMBO_DIAGS, line);
            continue;
        }
        generate_combinations(fout, cols, ncols, provspno_idx, combo_counter, sec_diag_indices, nsec);
        combo_counter += (1 << nsec);
    }
    fclose(fin);
    fclose(fout);
    return 0;
}

