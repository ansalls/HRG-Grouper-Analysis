// Outputs unique values (and optionally counts) from a specified column in a CSV file.
// Usage: unique_col_vals [-c] input.csv [output.csv] col

#include "csv_utils.h"
#include <direct.h>

#define MAX_UNIQUE 100000
#define MAX_VAL_LEN 1024

typedef struct {
    char val[MAX_VAL_LEN];
    int count;
} UniqueVal;

int main(int argc, char *argv[]) {
    char outfilename[1024];
    int with_count = 0;
    int verbose = 0;
    int arg_offset = 1;

    if (argc < 3) {
        print_usage_and_exit(argv[0], "[-c] [-v] input.csv [output.csv] col");
    }

    while (arg_offset < argc && argv[arg_offset][0] == '-' && argv[arg_offset][1] != '\0') {
        for (int i = 1; argv[arg_offset][i] != '\0'; ++i) {
            if (argv[arg_offset][i] == 'c') {
                with_count = 1;
                printf("Found -c flag\n");
            } else if (argv[arg_offset][i] == 'v') {
                verbose = 1;
                printf("Found -v flag\n");
            } else {
                fprintf_s(stderr, "Unknown flag: -%c\n", argv[arg_offset][i]);
                print_usage_and_exit(argv[0], "[-c] [-v] input.csv [output.csv] col");
            }
        }
        arg_offset++;
    }

    int positional = argc - arg_offset;
    printf("arg_offset = %d, positional = %d\n", arg_offset, positional);
    if (positional != 2 && positional != 3) {
        print_usage_and_exit(argv[0], "[-c] [-v] input.csv [output.csv] col");
    }
    const char *infilename = argv[arg_offset];
    int col;
    if (positional == 3) {
        strncpy_s(outfilename, sizeof(outfilename), argv[arg_offset + 1], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
        col = atoi(argv[arg_offset + 2]);
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
        col = atoi(argv[arg_offset + 1]);
    }
    if (col < 1) {
        fprintf_s(stderr, "Column position must be >= 1.\n");
        return 1;
    }

    printf("with_count = %d, verbose = %d\n", with_count, verbose);
    printf("Input file: %s\n", infilename);
    printf("Output file: %s\n", outfilename);
    printf("Column: %d\n", col);

    // Create directory for output if needed
    char outdir[1024];
    const char *last_slash = strrchr(outfilename, '\\');
    if (last_slash) {
        size_t dirlen = last_slash - outfilename;
        strncpy_s(outdir, sizeof(outdir), outfilename, dirlen);
        outdir[dirlen] = '\0';
        if (verbose) printf("Output directory: %s\n", outdir);

        if (_mkdir(outdir) != 0) {
            fprintf_s(stderr, "Error creating directory: %s\n", outdir);
            perror("_mkdir");
            return 1;
        }
    }

    FILE *fin = NULL, *fout = NULL;
    if (!open_input_output_files(infilename, outfilename, &fin, &fout)) {
        return 1;
    }

    if (verbose) printf("Processing...\n");
    char* line = (char*)malloc(MAX_LINE_LEN);
    if (!line) {
        fprintf_s(stderr, "Memory allocation failed\n");
        return 1;
    }

    char* header = (char*)malloc(MAX_LINE_LEN);
    if (!header) {
        fprintf_s(stderr, "Memory allocation failed\n");
        free(line);
        return 1;
    }

    char** cols = (char**)malloc(MAX_COLS * sizeof(char*));
    if (!cols) {
        fprintf_s(stderr, "Memory allocation failed\n");
        free(line);
        free(header);
        return 1;
    }

    UniqueVal* uniques = (UniqueVal*)malloc(MAX_UNIQUE * sizeof(UniqueVal));
    if (!uniques) {
        fprintf_s(stderr, "Memory allocation failed\n");
        free(line);
        free(header);
        free(cols);
        return 1;
    }

    // Handle header
    if (!fgets(header, MAX_LINE_LEN, fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        close_files(fin, fout);
        free(line);
        free(header);
        free(cols);
        free(uniques);
        return 1;
    }
    char *header_cols[MAX_COLS];
    int ncols = csv_split_line(header, header_cols, MAX_COLS);
    if (col > ncols) {
        fprintf_s(stderr, "Column position out of range. File has %d columns.\n", ncols);
        close_files(fin, fout);
        free(line);
        free(header);
        free(cols);
        free(uniques);
        return 1;
    }

    int unique_count = 0;

    // Process row
    int row_num = 1;
    while (fgets(line, MAX_LINE_LEN, fin)) {
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
        if (row_ncols < col) {
            if (verbose) printf("Skipping malformed row %d: %s\n", row_num, line);
            row_num++;
            continue;
        }

        char *val = cols[col-1];
        int found = 0;
        for (int i = 0; i < unique_count; ++i) {
            if (strcmp(uniques[i].val, val) == 0) {
                uniques[i].count++;
                found = 1;
                break;
            }
        }
        if (!found) {
            if (unique_count < MAX_UNIQUE) {
                strncpy_s(uniques[unique_count].val, sizeof(uniques[unique_count].val), val, _TRUNCATE);
                uniques[unique_count].count = 1;
                unique_count++;
            }
        }
        row_num++;
    }
    printf("Processed %d rows.\n", row_num-1);
    // Output unique values (and counts if requested)
    for (int i = 0; i < unique_count; ++i) {
        if (with_count)
            fprintf_s(fout, "%s,%d\n", uniques[i].val, uniques[i].count);
        else
            fprintf_s(fout, "%s\n", uniques[i].val);
    }
    printf("Wrote %d unique values.\n", unique_count);

    if (verbose) printf("Done. Unique values found: %d\n", unique_count);

    free(line);
    free(header);
    free(cols);
    free(uniques);

    close_files(fin, fout);
    return 0;
}