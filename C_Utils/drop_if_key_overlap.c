// Reads a CSV file, writes only the first row for each unique key (set of columns).
// Usage: drop_if_key_overlap [-k keycols] input.csv [output.csv]

#include "csv_utils.h"

#define MAX_KEY_COLS 100
#define MAX_KEY_STR 4096
#define MAX_KEY_SEEN 20000000

// Default columns
const char *default_key_cols[] = {
    "STARTAGE","SEX","CLASSPAT","ADMISORC","ADMIMETH","DISDEST","DISMETH","EPIDUR","MAINSPEF","NEOCARE","TRETSPEF",
    "DIAG_01","DIAG_02","DIAG_03","DIAG_04","DIAG_05","DIAG_06","DIAG_07","DIAG_08","DIAG_09","DIAG_10",
    "DIAG_11","DIAG_12","DIAG_13","DIAG_14","DIAG_15","DIAG_16","DIAG_17","DIAG_18","DIAG_19","DIAG_20",
    "SpellHRG"
};
#define DEFAULT_KEY_COLS_COUNT (sizeof(default_key_cols)/sizeof(default_key_cols[0]))

void trim(char *s) {
    char *end;
    while (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n') s++;
    end = s + strlen(s) - 1;
    while (end > s && (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')) *end-- = 0;
}

int parse_keycols(const char *arg, int *key_indexes, char *key_names[MAX_KEY_COLS], int *is_index_mode) {
    int count = 0;
    char buf[2048];
    strncpy_s(buf, sizeof(buf), arg, _TRUNCATE);
    buf[sizeof(buf)-1] = 0;
    char *p = buf;
    bool all_int = true;
    // First check if all comma-delimited tokens are integers
    while (*p) {
        while (*p == ',') p++;
        if (!*p) break;
        char *start = p;
        while (*p && *p != ',') p++;
        char tmp = *p;
        *p = 0;
        trim(start);
        if (*start == 0 || strspn(start, "0123456789") != strlen(start)) {
            all_int = false;
            break;
        }
        *p = tmp;
        if (*p) p++;
    }
    p = buf;
    count = 0;
    if (all_int) {
        *is_index_mode = 1;
        while (*p && count < MAX_KEY_COLS) {
            while (*p == ',') p++;
            if (!*p) break;
            char *start = p;
            while (*p && *p != ',') p++;
            char tmp = *p;
            *p = 0;
            trim(start);
            key_indexes[count++] = atoi(start);
            *p = tmp;
            if (*p) p++;
        }
    } else {
        *is_index_mode = 0;
        while (*p && count < MAX_KEY_COLS) {
            while (*p == ',') p++;
            if (!*p) break;
            char *start = p;
            while (*p && *p != ',') p++;
            char tmp = *p;
            *p = 0;
            trim(start);
            key_names[count] = (char*)malloc(strlen(start)+1);
            if (key_names[count]) {
                strncpy_s(key_names[count], strlen(start)+1, start, _TRUNCATE);
            }
            count++;
            *p = tmp;
            if (*p) p++;
        }
    }
    return count;
}

int find_col_index(const char *name, char *header_cols[], int ncols) {
    int found = -1;
    for (int i = 0; i < ncols; ++i) {
        if (strcmp(header_cols[i], name) == 0) {
            if (found != -1) {
                fprintf_s(stderr, "[WARNING] Duplicate column header \"%s\" found at index %d (using last instance at %d)\n", name, found+1, i+1);
            }
            found = i;
        }
    }
    if (found == -1) {
        fprintf_s(stderr, "[ERROR] Column header \"%s\" not found in input file.\n", name);
    }
    return found;
}

// Build key from selected columns from which we'll determine "overlap"
void build_key(char *out, size_t outlen, char *cols[], int key_indexes[], int key_count) {
    out[0] = 0;
    for (int i = 0; i < key_count; ++i) {
        if (i > 0) strncat_s(out, outlen, "|", _TRUNCATE);
        strncat_s(out, outlen, cols[key_indexes[i]], _TRUNCATE);
    }
}

typedef struct {
    char key[MAX_KEY_STR];
} KeySeen;

int main(int argc, char *argv[]) {
    char outfilename[1024];
    int key_indexes[MAX_KEY_COLS];
    char *key_names[MAX_KEY_COLS];
    int key_count = 0;
    int is_index_mode = 0;
    int use_default_key = 1;
    int argi = 1;

    if (argc > 2 && strcmp(argv[1], "-k") == 0) {
        use_default_key = 0;
        if (argc < 4) {
            print_usage_and_exit(argv[0], "[-k keycols] input.csv [output.csv]");
        }
        key_count = parse_keycols(argv[2], key_indexes, key_names, &is_index_mode);
        argi = 3;
    }

    if (argc - argi < 1 || argc - argi > 2) {
        print_usage_and_exit(argv[0], "[-k keycols] input.csv [output.csv]");
    }
    const char *infilename = argv[argi];
    if (argc - argi == 2) {
        strncpy_s(outfilename, sizeof(outfilename), argv[argi+1], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        make_output_filename(infilename, outfilename, sizeof(outfilename));
    }

    FILE *fin = NULL, *fout = NULL;
    if (!open_input_output_files(infilename, outfilename, &fin, &fout)) {
        if (!use_default_key && !is_index_mode) {
            for (int i = 0; i < key_count; ++i) free(key_names[i]);
        }
        return 1;
    }

    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0;

    // Handle header
    if (!fgets(line, sizeof(line), fin)) {
        fprintf_s(stderr, "Empty input file.\n");
        close_files(fin, fout);
        if (!use_default_key && !is_index_mode) {
            for (int i = 0; i < key_count; ++i) free(key_names[i]);
        }
        return 1;
    }
    fputs(line, fout);

    // Get column names
    char header[MAX_LINE_LEN];
    strncpy_s(header, sizeof(header), line, _TRUNCATE);
    header[sizeof(header)-1] = 0;
    ncols = csv_split_line(header, cols, MAX_COLS);

    // Determine key column indexes
    if (use_default_key) {
        key_count = (int)DEFAULT_KEY_COLS_COUNT;
        for (int i = 0; i < key_count; ++i) {
            int idx = find_col_index(default_key_cols[i], cols, ncols);
            if (idx < 0) {
                close_files(fin, fout);
                return 1;
            }
            key_indexes[i] = idx;
        }
    } else if (!is_index_mode) {
        for (int i = 0; i < key_count; ++i) {
            int idx = find_col_index(key_names[i], cols, ncols);
            if (idx < 0) {
                close_files(fin, fout);
                for (int j = 0; j < key_count; ++j) free(key_names[j]);
                return 1;
            }
            key_indexes[i] = idx;
        }
        for (int i = 0; i < key_count; ++i) free(key_names[i]);
    } else {
        for (int i = 0; i < key_count; ++i) {
            if (key_indexes[i] < 1 || key_indexes[i] > ncols) {
                fprintf_s(stderr, "[ERROR] Key column index %d out of range (file has %d columns)\n", key_indexes[i], ncols);
                close_files(fin, fout);
                return 1;
            }
            key_indexes[i] -= 1;
        }
    }

    KeySeen *seen = (KeySeen*)malloc(sizeof(KeySeen) * MAX_KEY_SEEN);
    if (!seen) {
        fprintf_s(stderr, "Memory allocation failed\n");
        close_files(fin, fout);
        return 1;
    }
    int seen_count = 0;

    // Process row
    int total_rows = 0, written_rows = 0, skipped_rows = 0;
    while (fgets(line, sizeof(line), fin)) {
        total_rows++;
        line[strcspn(line, "\r\n")] = 0;
        char row[MAX_LINE_LEN];
        strncpy_s(row, sizeof(row), line, _TRUNCATE);
        row[sizeof(row)-1] = 0;
        int row_ncols = csv_split_line(row, cols, MAX_COLS);
        if (row_ncols < ncols) continue;

        char key[MAX_KEY_STR];
        build_key(key, sizeof(key), cols, key_indexes, key_count);

        int found = 0;
        for (int i = 0; i < seen_count; ++i) {
            if (strcmp(seen[i].key, key) == 0) {
                found = 1;
                break;
            }
        }
        if (!found) {
            if (seen_count < MAX_KEY_SEEN) {
                strncpy_s(seen[seen_count].key, sizeof(seen[seen_count].key), key, _TRUNCATE);
                seen_count++;
            }
            csv_write_row(fout, cols, ncols);
            written_rows++;
        } else {
            skipped_rows++;
        }
    }
    free(seen);
    close_files(fin, fout);
    printf("[INFO] Processed %d rows, wrote %d unique, skipped %d duplicates.\n", total_rows, written_rows, skipped_rows);
    return 0;
}
