import os
import sys
import argparse
import logging
import pandas as pd
from tqdm import tqdm


def get_sheet_names(excel_path):
    xls = pd.ExcelFile(excel_path)
    return xls.sheet_names


def check_conflicts(sheet_names, target_dir):
    conflicts = []
    for sheet in sheet_names:
        csv_path = os.path.join(target_dir, f"{sheet}.csv")
        if os.path.exists(csv_path):
            conflicts.append(csv_path)
    return conflicts


def prompt_user_for_conflicts(conflicts):
    print("Conflicting files detected:")
    for f in conflicts:
        print(f"  {f}")
    while True:
        resp = input("Choose action: [s]kip conflicting files, [o]verwrite existing files: "
                     ).strip().lower()
        if resp in ("s", "o"):
            return resp
        print("Invalid input. Please enter 's' or 'o'.")


def convert_sheets_to_csv(excel_path, target_dir, skip_conflicts):
    xls = pd.ExcelFile(excel_path)
    sheet_names = xls.sheet_names
    for sheet in tqdm(sheet_names, desc="Converting sheets", unit="sheet"):
        csv_path = os.path.join(target_dir, f"{sheet}.csv")
        if skip_conflicts and os.path.exists(csv_path):
            logging.info("Skipping existing file: %s", csv_path)
            continue
        try:
            df = pd.read_excel(xls, sheet_name=sheet)
            df.to_csv(csv_path, index=False)
            logging.info("Saved sheet '%s' to %s", sheet, csv_path)
        except Exception as e:
            logging.error("Failed to convert sheet '%s': %s", sheet, e)


def main():
    parser = argparse.ArgumentParser(description="Convert all sheets in an Excel workbook to CSV files.")
    parser.add_argument("excel_file", help="Path to the Excel workbook.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    excel_path = args.excel_file
    if not os.path.isfile(excel_path):
        logging.error("File not found: %s", excel_path)
        sys.exit(1)

    target_dir = os.path.dirname(os.path.abspath(excel_path))
    logging.info("Reading Excel file: %s", excel_path)
    sheet_names = get_sheet_names(excel_path)
    logging.info("Found sheets: %s", sheet_names)

    conflicts = check_conflicts(sheet_names, target_dir)
    skip_conflicts = False
    if conflicts:
        action = prompt_user_for_conflicts(conflicts)
        skip_conflicts = (action == "s")
    else:
        logging.info("No conflicting CSV files found.")

    convert_sheets_to_csv(excel_path, target_dir, skip_conflicts)
    logging.info("Done.")


if __name__ == "__main__":
    main()
