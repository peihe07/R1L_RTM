#!/usr/bin/env python3
"""
Remove # symbols from Melco ID in CFTS Excel files and Feature-ID in TestCase Excel file.
"""
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime
import shutil


class HashSymbolCleaner:
    """Clean # symbols from Excel files."""

    def __init__(self):
        """Initialize cleaner."""
        self.report = {
            'cfts_files_processed': 0,
            'cfts_records_cleaned': 0,
            'testcase_files_processed': 0,
            'testcase_records_cleaned': 0,
            'errors': []
        }

    def clean_cfts_excel(self, file_path: Path, backup: bool = True) -> int:
        """
        Clean # symbols from Melco ID column in CFTS Excel file.

        Args:
            file_path: Path to CFTS Excel file
            backup: Whether to create backup file

        Returns:
            Number of records cleaned
        """
        try:
            # Create backup
            if backup:
                backup_path = file_path.parent / f"{file_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
                shutil.copy2(file_path, backup_path)
                print(f"  Backup created: {backup_path.name}")

            # Read Excel file
            df = pd.read_excel(file_path)

            # Check if Melco Id column exists
            if 'Melco Id' not in df.columns:
                print(f"  Warning: 'Melco Id' column not found in {file_path.name}")
                return 0

            # Count records with # before cleaning
            has_hash_before = df['Melco Id'].astype(str).str.contains('#', na=False).sum()

            if has_hash_before == 0:
                print(f"  No # symbols found in {file_path.name}")
                return 0

            # Remove # symbols from Melco Id column
            df['Melco Id'] = df['Melco Id'].astype(str).str.replace('#', '', regex=False)

            # Replace 'nan' strings back to empty
            df['Melco Id'] = df['Melco Id'].replace('nan', '')

            # Save back to Excel
            df.to_excel(file_path, index=False)

            print(f"  Cleaned {has_hash_before} records with # symbols")
            return has_hash_before

        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            print(f"  ERROR: {error_msg}")
            self.report['errors'].append(error_msg)
            return 0

    def clean_testcase_excel(self, file_path: Path, backup: bool = True) -> int:
        """
        Clean # symbols from Feature-ID column in TestCase Excel file.

        Args:
            file_path: Path to TestCase Excel file
            backup: Whether to create backup file

        Returns:
            Number of records cleaned
        """
        try:
            # Create backup
            if backup:
                backup_path = file_path.parent / f"{file_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
                shutil.copy2(file_path, backup_path)
                print(f"  Backup created: {backup_path.name}")

            # Read Excel file
            df = pd.read_excel(file_path)

            # Check if Feature-ID column exists
            if 'Feature-ID' not in df.columns:
                print(f"  Warning: 'Feature-ID' column not found in {file_path.name}")
                return 0

            # Count records with # before cleaning
            has_hash_before = df['Feature-ID'].astype(str).str.contains('#', na=False).sum()

            if has_hash_before == 0:
                print(f"  No # symbols found in {file_path.name}")
                return 0

            # Remove # symbols from Feature-ID column
            df['Feature-ID'] = df['Feature-ID'].astype(str).str.replace('#', '', regex=False)

            # Replace 'nan' strings back to empty
            df['Feature-ID'] = df['Feature-ID'].replace('nan', '')

            # Save back to Excel
            df.to_excel(file_path, index=False)

            print(f"  Cleaned {has_hash_before} records with # symbols")
            return has_hash_before

        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            print(f"  ERROR: {error_msg}")
            self.report['errors'].append(error_msg)
            return 0

    def process_cfts_folder(self, cfts_folder: Path, backup: bool = True):
        """Process all CFTS Excel files in folder."""
        print("=" * 80)
        print("PROCESSING CFTS EXCEL FILES")
        print("=" * 80)

        # Find all CFTS Excel files
        excel_files = []
        for ext in ['.xlsx', '.xls']:
            for file in cfts_folder.iterdir():
                if file.name.startswith('CFTS') and file.name.endswith(ext):
                    excel_files.append(file)

        excel_files = sorted(excel_files)
        print(f"Found {len(excel_files)} CFTS Excel files\n")

        # Process each file
        for idx, file_path in enumerate(excel_files, 1):
            print(f"[{idx}/{len(excel_files)}] Processing: {file_path.name}")
            cleaned_count = self.clean_cfts_excel(file_path, backup=backup)
            if cleaned_count > 0:
                self.report['cfts_files_processed'] += 1
                self.report['cfts_records_cleaned'] += cleaned_count

    def process_testcase_file(self, testcase_file: Path, backup: bool = True):
        """Process TestCase Excel file."""
        print("\n" + "=" * 80)
        print("PROCESSING TESTCASE EXCEL FILE")
        print("=" * 80)
        print(f"Processing: {testcase_file.name}")

        cleaned_count = self.clean_testcase_excel(testcase_file, backup=backup)
        if cleaned_count > 0:
            self.report['testcase_files_processed'] += 1
            self.report['testcase_records_cleaned'] += cleaned_count

    def print_summary(self):
        """Print cleanup summary."""
        print("\n" + "=" * 80)
        print("CLEANUP SUMMARY")
        print("=" * 80)
        print(f"CFTS files processed: {self.report['cfts_files_processed']}")
        print(f"CFTS records cleaned: {self.report['cfts_records_cleaned']}")
        print(f"\nTestCase files processed: {self.report['testcase_files_processed']}")
        print(f"TestCase records cleaned: {self.report['testcase_records_cleaned']}")

        if self.report['errors']:
            print(f"\nErrors encountered: {len(self.report['errors'])}")
            for error in self.report['errors']:
                print(f"  - {error}")

        print("=" * 80)


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python cleanup_hash_symbols.py <cfts_folder> <testcase_file>")
        print("\nExample: python cleanup_hash_symbols.py ../data/CFTS ../data/R1L_TestCase.xlsx")
        sys.exit(1)

    cfts_folder = Path(sys.argv[1])
    testcase_file = Path(sys.argv[2])

    # Validate paths
    if not cfts_folder.is_dir():
        print(f"Error: {cfts_folder} is not a valid directory")
        sys.exit(1)

    if not testcase_file.is_file():
        print(f"Error: {testcase_file} is not a valid file")
        sys.exit(1)

    # Create cleaner and process files
    cleaner = HashSymbolCleaner()
    cleaner.process_cfts_folder(cfts_folder, backup=True)
    cleaner.process_testcase_file(testcase_file, backup=True)
    cleaner.print_summary()


if __name__ == "__main__":
    main()
