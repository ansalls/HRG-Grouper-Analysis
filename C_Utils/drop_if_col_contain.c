// Reads a CSV file, copies lines to a new file only if a specified column
//  contains a given string (substring match).
// Usage: drop_if_col_contain [-i] [-v] [-n] input.csv [output.csv] col match_term

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LINE_LEN 100000
#define MAX_COLS 400
#define MAX_MATCH_TERMS 1000

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

// Case-insensitive strstr
char *strcasestr_local(const char *source, const char *substr) {
    if (!*substr) return (char *)source;
    for (; *source; ++source) {
        const char *s = source, *n = substr;
        while (*s && *n && tolower((unsigned char)*s) == tolower((unsigned char)*n)) {
            ++s; ++n;
        }
        if (!*n) return (char *)source;
    }
    return NULL;
}

void str_tolower(char *s) {
    for (; *s; ++s) *s = (char)tolower((unsigned char)*s);
}

typedef struct {
    char term[256];
    int count;
} MatchCount;

int main(int argc, char *argv[]) {
    char outfilename[1024];
    bool case_insensitive = false;
    bool verbose = false;
    bool not_flag = false;
    int arg_offset = 0;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-i") == 0) {
            case_insensitive = true;
            arg_offset++;
        } else if (strcmp(argv[i], "-v") == 0) {
            verbose = true;
            arg_offset++;
        } else if (strcmp(argv[i], "-n") == 0) {
            not_flag = true;
            arg_offset++;
        } else {
            break;
        }
    }

    if ((argc != 4 + arg_offset) && (argc != 5 + arg_offset)) {
        fprintf_s(stderr, "Usage: %s [-i] [-v] [-n] input.csv [output.csv] col match_term\n", argv[0]);
        return 1;
    }
    const char *infilename = argv[1 + arg_offset];
    int col;
    char match_term[256];
    if (argc == 5 + arg_offset) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2 + arg_offset], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
        col = atoi(argv[3 + arg_offset]);
        strncpy_s(match_term, sizeof(match_term), argv[4 + arg_offset], _TRUNCATE);
        match_term[sizeof(match_term)-1] = 0;
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
        col = atoi(argv[2 + arg_offset]);
        strncpy_s(match_term, sizeof(match_term), argv[3 + arg_offset], _TRUNCATE);
        match_term[sizeof(match_term)-1] = 0;
    }
    if (col < 1) {
        fprintf_s(stderr, "Column position must be >= 1.\n");
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
    if (col > ncols) {
        fprintf_s(stderr, "Column position out of range. File has %d columns.\n", ncols);
        fclose(fin);
        fclose(fout);
        return 1;
    }

    char match_term_cmp[256];
    strncpy_s(match_term_cmp, sizeof(match_term_cmp), match_term, _TRUNCATE);
    match_term_cmp[sizeof(match_term_cmp)-1] = 0;
    if (case_insensitive) str_tolower(match_term_cmp);

    int match_count = 0;

    // Process row
    while (fgets(line, sizeof(line), fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) continue;

        bool found = false;
        char *cell = cols[col-1];
        if (case_insensitive) {
            char cell_lc[MAX_LINE_LEN];
            strncpy_s(cell_lc, sizeof(cell_lc), cell, _TRUNCATE);
            cell_lc[sizeof(cell_lc)-1] = 0;
            str_tolower(cell_lc);
            if (strcasestr_local(cell_lc, match_term_cmp)) {
                found = true;
            }
        } else {
            if (strstr(cell, match_term_cmp)) {
                found = true;
            }
        }
        if ((!not_flag && found) || (not_flag && !found)) {
            match_count++;
            continue;
        }
        fprintf_s(fout, "%s\n", line);
    }
    fclose(fin);
    fclose(fout);

    if (verbose) {
        printf("Matched term: \"%s\" | Count: %d\n", match_term, match_count);
    }
    return 0;
}
