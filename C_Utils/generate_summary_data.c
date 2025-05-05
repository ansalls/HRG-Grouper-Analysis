// Generates a summary of counts for specified columns and their combinations in a CSV file.
// Usage: generate_summary_data input.csv [summary_output.txt]

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN 100000
#define MAX_COLS 400

// Bit of a mess I've made trying to fix some memory issues, but is so specific to
//  this particular use case that there's little point in spending time to clean it up.
typedef struct {
    char *key1;
    char *key2;
    char *key3;
    int count;
} CountEntry;

typedef struct {
    CountEntry *data;
    int size;
    int cap;
} CountTable;

void ct_init(CountTable *ct) {
    ct->data = NULL;
    ct->size = 0;
    ct->cap = 0;
}
void ct_free(CountTable *ct) {
    for (int i = 0; i < ct->size; ++i) {
        if (ct->data[i].key1) free(ct->data[i].key1);
        if (ct->data[i].key2) free(ct->data[i].key2);
        if (ct->data[i].key3) free(ct->data[i].key3);
    }
    free(ct->data);
}
void ct_grow(CountTable *ct) {
    if (ct->size >= ct->cap) {
        ct->cap = ct->cap ? ct->cap * 2 : 1024;
        ct->data = (CountEntry*)realloc(ct->data, ct->cap * sizeof(CountEntry));
        if (!ct->data) { fprintf_s(stderr, "Out of memory\n"); exit(1); }
    }
}
int ct_find(CountTable *ct, const char *k1, const char *k2, const char *k3) {
    for (int i = 0; i < ct->size; ++i) {
        if ((!k1 && !ct->data[i].key1) || (k1 && ct->data[i].key1 && strcmp(k1, ct->data[i].key1) == 0)) {
            if ((!k2 && !ct->data[i].key2) || (k2 && ct->data[i].key2 && strcmp(k2, ct->data[i].key2) == 0)) {
                if ((!k3 && !ct->data[i].key3) || (k3 && ct->data[i].key3 && strcmp(k3, ct->data[i].key3) == 0)) {
                    return i;
                }
            }
        }
    }
    return -1;
}
void ct_inc(CountTable *ct, const char *k1, const char *k2, const char *k3) {
    int idx = ct_find(ct, k1, k2, k3);
    if (idx >= 0) {
        ct->data[idx].count++;
        return;
    }
    ct_grow(ct);
    ct->data[ct->size].key1 = k1 ? _strdup(k1) : NULL;
    ct->data[ct->size].key2 = k2 ? _strdup(k2) : NULL;
    ct->data[ct->size].key3 = k3 ? _strdup(k3) : NULL;
    ct->data[ct->size].count = 1;
    ct->size++;
}

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

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf_s(stderr, "Usage: %s input.csv [summary_output.txt]\n", argv[0]);
        return 1;
    }
    const char *infilename = argv[1];
    char outfilename[1024];
    if (argc >= 3) {
        strncpy_s(outfilename, sizeof(outfilename), argv[2], _TRUNCATE);
        outfilename[sizeof(outfilename)-1] = 0;
    } else {
        const char *dot = strrchr(infilename, '.');
        size_t base_len = dot && dot != infilename ? (size_t)(dot - infilename) : strlen(infilename);
        if (base_len > sizeof(outfilename) - 14) base_len = sizeof(outfilename) - 14; // leave space for _summary.txt + null
        strncpy_s(outfilename, sizeof(outfilename), infilename, base_len);
        outfilename[base_len] = '\0';
        strncat_s(outfilename, sizeof(outfilename), "_summary.txt", _TRUNCATE);
    }

    FILE *fin = NULL;
    FILE *fout = NULL;
    if (fopen_s(&fin, infilename, "r") != 0 || !fin) {
        fprintf_s(stderr, "Could not open input file\n");
        return 1;
    }
    if (fopen_s(&fout, outfilename, "w") != 0 || !fout) {
        fprintf_s(stderr, "Could not open output file\n");
        fclose(fin);
        return 1;
    }

    char line[MAX_LINE_LEN];
    char *cols[MAX_COLS];
    int ncols = 0;
    int diag_idxs[MAX_COLS], ndiag = 0;
    int oper_idxs[MAX_COLS], noper = 0;
    int spellhrg_idx = -1, tretspef_idx = -1, mainspef_idx = -1, domproc_idx = -1;

    if (!fgets(line, sizeof(line), fin)) { fprintf_s(stderr, "Empty input file\n"); fclose(fin); fclose(fout); return 1; }
    line[strcspn(line, "\r\n")] = 0;
    ncols = split_line(line, cols, MAX_COLS);
    for (int i = 0; i < ncols; ++i) {
        if (strncmp(cols[i], "DIAG_", 5) == 0) diag_idxs[ndiag++] = i;
        if (strncmp(cols[i], "OPER_", 5) == 0) oper_idxs[noper++] = i;
        if (strcmp(cols[i], "SpellHRG") == 0) spellhrg_idx = i;
        if (strcmp(cols[i], "TRETSPEF") == 0) tretspef_idx = i;
        if (strcmp(cols[i], "MAINSPEF") == 0) mainspef_idx = i;
        if (strcmp(cols[i], "DominantProcedure") == 0) domproc_idx = i;
    }
    if (ndiag == 0 || spellhrg_idx < 0) {
        fprintf_s(stderr, "Missing DIAG_XX or SpellHRG columns\n");
        fclose(fin); fclose(fout); return 1;
    }

    // Prepare count tables
    CountTable diag_counts, diag_spellhrg_counts, diag_oper_counts, spellhrg_counts, spellhrg_chap_counts;
    CountTable spellhrg_tretspef, spellhrg_mainspef, spellhrgchap_tretspef, spellhrgchap_mainspef;
    CountTable domproc_spellhrg, domproc_spellhrgchap, domproc_spellhrgroot, domproc_tretspef, domproc_mainspef;
    ct_init(&diag_counts); ct_init(&diag_spellhrg_counts); ct_init(&diag_oper_counts); ct_init(&spellhrg_counts); ct_init(&spellhrg_chap_counts);
    ct_init(&spellhrg_tretspef); ct_init(&spellhrg_mainspef); ct_init(&spellhrgchap_tretspef); ct_init(&spellhrgchap_mainspef);
    ct_init(&domproc_spellhrg); ct_init(&domproc_spellhrgchap); ct_init(&domproc_spellhrgroot); ct_init(&domproc_tretspef); ct_init(&domproc_mainspef);

    // Process row
    long row_counter = 0;
    while (fgets(line, sizeof(line), fin)) {
        row_counter++;
        if (row_counter % 10000 == 0) {
            printf("Processed %ld rows...\n", row_counter);
        }
        line[strcspn(line, "\r\n")] = 0;
        split_line(line, cols, MAX_COLS);
        // DIAG code counts
        for (int d = 0; d < ndiag; ++d) {
            char *diag = cols[diag_idxs[d]];
            if (diag && diag[0]) {
                ct_inc(&diag_counts, diag, NULL, NULL);
                // DIAG + SpellHRG
                ct_inc(&diag_spellhrg_counts, diag, cols[spellhrg_idx], NULL);
            }
        }
        // DIAG + OPER code pairs
        for (int d = 0; d < ndiag; ++d) {
            char *diag = cols[diag_idxs[d]];
            if (!diag || !diag[0]) continue;
            int any_oper = 0;
            for (int o = 0; o < noper; ++o) {
                char *oper = cols[oper_idxs[o]];
                if (oper && oper[0]) {
                    ct_inc(&diag_oper_counts, diag, oper, NULL);
                    any_oper = 1;
                }
            }
            if (!any_oper) {
                ct_inc(&diag_oper_counts, diag, "NULL", NULL);
            }
        }
        // SpellHRG counts
        char *spellhrg = cols[spellhrg_idx];
        if (spellhrg && spellhrg[0]) {
            ct_inc(&spellhrg_counts, spellhrg, NULL, NULL);
            // SpellHRG chapter
            char chap[3] = {0};
            strncpy_s(chap, sizeof(chap), spellhrg, 2);
            ct_inc(&spellhrg_chap_counts, chap, NULL, NULL);
            // SpellHRG by TRETSPEF/MAINSPEF
            if (tretspef_idx >= 0 && cols[tretspef_idx] && cols[tretspef_idx][0])
                ct_inc(&spellhrg_tretspef, spellhrg, cols[tretspef_idx], NULL);
            if (mainspef_idx >= 0 && cols[mainspef_idx] && cols[mainspef_idx][0])
                ct_inc(&spellhrg_mainspef, spellhrg, cols[mainspef_idx], NULL);
            // SpellHRG chapter by TRETSPEF/MAINSPEF
            if (tretspef_idx >= 0 && cols[tretspef_idx] && cols[tretspef_idx][0])
                ct_inc(&spellhrgchap_tretspef, chap, cols[tretspef_idx], NULL);
            if (mainspef_idx >= 0 && cols[mainspef_idx] && cols[mainspef_idx][0])
                ct_inc(&spellhrgchap_mainspef, chap, cols[mainspef_idx], NULL);
        }
        // DominantProcedure by varius columns
        if (domproc_idx >= 0 && cols[domproc_idx] && cols[domproc_idx][0]) {
            char *domproc = cols[domproc_idx];
            if (spellhrg && spellhrg[0]) {
                ct_inc(&domproc_spellhrg, domproc, spellhrg, NULL);
                char chap[3] = {0}; strncpy_s(chap, sizeof(chap), spellhrg, 2);
                ct_inc(&domproc_spellhrgchap, domproc, chap, NULL);
                char root[5] = {0}; strncpy_s(root, sizeof(root), spellhrg, 4);
                ct_inc(&domproc_spellhrgroot, domproc, root, NULL);
            }
            if (tretspef_idx >= 0 && cols[tretspef_idx] && cols[tretspef_idx][0])
                ct_inc(&domproc_tretspef, domproc, cols[tretspef_idx], NULL);
            if (mainspef_idx >= 0 && cols[mainspef_idx] && cols[mainspef_idx][0])
                ct_inc(&domproc_mainspef, domproc, cols[mainspef_idx], NULL);
        }
    }
    printf("Processed %ld rows (total).\n", row_counter);
    fclose(fin);

    // Flush the summaries
    #define PRINT_TABLE(title, tab, k1, k2, k3) \
        fprintf_s(fout, "\n[%s]\n", title); \
        for (int i = 0; i < (tab).size; ++i) { \
            fprintf_s(fout, "%s", (tab).data[i].key1 ? (tab).data[i].key1 : ""); \
            if (k2 && (tab).data[i].key2) fprintf_s(fout, ",%s", (tab).data[i].key2); \
            if (k3 && (tab).data[i].key3) fprintf_s(fout, ",%s", (tab).data[i].key3); \
            fprintf_s(fout, ",%d\n", (tab).data[i].count); \
        }

    PRINT_TABLE("DIAG code counts", diag_counts, 1, 0, 0)
    PRINT_TABLE("DIAG+SpellHRG counts", diag_spellhrg_counts, 1, 1, 0)
    PRINT_TABLE("DIAG+OPER code pairs", diag_oper_counts, 1, 1, 0)
    PRINT_TABLE("SpellHRG counts", spellhrg_counts, 1, 0, 0)
    PRINT_TABLE("SpellHRG chapter counts", spellhrg_chap_counts, 1, 0, 0)
    PRINT_TABLE("SpellHRG by TRETSPEF", spellhrg_tretspef, 1, 1, 0)
    PRINT_TABLE("SpellHRG by MAINSPEF", spellhrg_mainspef, 1, 1, 0)
    PRINT_TABLE("SpellHRG chapter by TRETSPEF", spellhrgchap_tretspef, 1, 1, 0)
    PRINT_TABLE("SpellHRG chapter by MAINSPEF", spellhrgchap_mainspef, 1, 1, 0)
    PRINT_TABLE("DominantProcedure by SpellHRG", domproc_spellhrg, 1, 1, 0)
    PRINT_TABLE("DominantProcedure by SpellHRG chapter", domproc_spellhrgchap, 1, 1, 0)
    PRINT_TABLE("DominantProcedure by SpellHRG root", domproc_spellhrgroot, 1, 1, 0)
    PRINT_TABLE("DominantProcedure by TRETSPEF", domproc_tretspef, 1, 1, 0)
    PRINT_TABLE("DominantProcedure by MAINSPEF", domproc_mainspef, 1, 1, 0)

    // Ahh, the cleanup
    ct_free(&diag_counts); ct_free(&diag_spellhrg_counts); ct_free(&diag_oper_counts); ct_free(&spellhrg_counts); ct_free(&spellhrg_chap_counts);
    ct_free(&spellhrg_tretspef); ct_free(&spellhrg_mainspef); ct_free(&spellhrgchap_tretspef); ct_free(&spellhrgchap_mainspef);
    ct_free(&domproc_spellhrg); ct_free(&domproc_spellhrgchap); ct_free(&domproc_spellhrgroot); ct_free(&domproc_tretspef); ct_free(&domproc_mainspef);

    fclose(fout);
    printf("Summary written to %s\n", outfilename);
    return 0;
}