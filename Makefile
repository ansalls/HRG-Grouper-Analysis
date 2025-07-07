# Basic makefile for compiling C utilities in C_Utils directory

CC = clang
CFLAGS = -Wall -Wextra -Werror -g -O0
UTILS_DIR = C_Utils

# List of utilities to build...
UTILS = append_diag col_substring_compare drop_if_col_contain drop_if_cols_dif drop_if_diags_exceed drop_if_key_overlap generate_code_combos_file generate_summary_data one_hot_encode_diags shift_diags_left split_field unique_col_vals

all: $(UTILS:%=$(UTILS_DIR)/%.exe)

$(UTILS_DIR)/append_diag.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/append_diag.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/col_substring_compare.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/col_substring_compare.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/drop_if_col_contain.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/drop_if_col_contain.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/drop_if_cols_dif.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/drop_if_cols_dif.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/drop_if_diags_exceed.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/drop_if_diags_exceed.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/drop_if_key_overlap.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/drop_if_key_overlap.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/generate_code_combos_file.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/generate_code_combos_file.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/generate_summary_data.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/generate_summary_data.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/one_hot_encode_diags.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/one_hot_encode_diags.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/shift_diags_left.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/shift_diags_left.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/split_field.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/split_field.c
	$(CC) $(CFLAGS) $^ -o $@

$(UTILS_DIR)/unique_col_vals.exe: $(UTILS_DIR)/csv_utils.c $(UTILS_DIR)/unique_col_vals.c
	$(CC) $(CFLAGS) $^ -o $@

clean:
	rm -f $(UTILS_DIR)/*.exe
