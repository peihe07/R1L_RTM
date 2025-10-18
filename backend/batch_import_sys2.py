#!/usr/bin/env python3
"""Batch import SYS.2 requirements from Excel files."""
import pandas as pd
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

from app.db.database import engine, SessionLocal, Base
from app.models.sys2_requirement import SYS2RequirementDB, SYS2Requirement


class SYS2Importer:
    """Batch import SYS.2 Excel files."""

    def __init__(self, excel_folder: str):
        """
        Initialize SYS.2 importer.

        Args:
            excel_folder: Path to folder containing SYS.2 Excel files
        """
        self.excel_folder = Path(excel_folder)
        self.report = {
            'total_files': 0,
            'success_files': [],
            'failed_files': [],
            'total_records': 0,
            'inserted_records': 0,
            'skipped_records': 0,
            'errors': []
        }

    def find_excel_files(self) -> List[Path]:
        """Find all SYS.2 Excel files in the folder."""
        excel_files = []
        for ext in ['.xlsx', '.xls']:
            for file in self.excel_folder.iterdir():
                if file.name.startswith('R1L_SYS.2') and file.name.endswith(ext):
                    excel_files.append(file)
        return sorted(excel_files)

    def extract_cfts_from_filename(self, filename: str) -> Tuple[str, str]:
        """
        Extract CFTS number and name from filename.

        Example: R1L_SYS.2_CFTS016_Anti-Theft.xlsx -> (CFTS016, Anti-Theft)
        """
        # Extract CFTS number
        cfts_match = re.search(r'CFTS\d+', filename)
        cfts_id = cfts_match.group(0) if cfts_match else ''

        # Extract CFTS name (between CFTS number and .xlsx)
        name_match = re.search(r'CFTS\d+_(.+?)\.xlsx', filename)
        cfts_name = name_match.group(1).strip() if name_match else ''

        return cfts_id, cfts_name

    def parse_excel_file(self, file_path: Path) -> Tuple[List[Dict], int]:
        """
        Parse a single SYS.2 Excel file.

        Returns:
            Tuple of (parsed_data, total_count)
        """
        try:
            # Extract CFTS info from filename
            cfts_id, cfts_name = self.extract_cfts_from_filename(file_path.name)
            if not cfts_id:
                raise Exception(f"Could not extract CFTS number from filename: {file_path.name}")

            # Read Excel file
            df = pd.read_excel(file_path)
            total_count = len(df)

            # Convert to list of dicts
            data = []
            for _, row in df.iterrows():
                # Get Melco ID (要件ID)
                melco_id = str(row.get('要件ID', '')).strip()
                if not melco_id or melco_id == 'nan':
                    continue  # Skip rows without Melco ID

                # Extract all fields
                record = {
                    'melco_id': melco_id,
                    'cfts_id': cfts_id,
                    'cfts_name': cfts_name,
                    'requirement_en': str(row.get('要件(英語)', '')).strip() if pd.notna(row.get('要件(英語)')) else '',
                    'reason_en': str(row.get('理由(英語)', '')).strip() if pd.notna(row.get('理由(英語)')) else '',
                    'supplement_en': str(row.get('補足(英語)', '')).strip() if pd.notna(row.get('補足(英語)')) else '',
                    'confirmation_phase': str(row.get('確認フェーズ', '')).strip() if pd.notna(row.get('確認フェーズ')) else '',
                    'verification_criteria': str(row.get('検証基準', '')).strip() if pd.notna(row.get('検証基準')) else '',
                    'type': str(row.get('種別', '')).strip() if pd.notna(row.get('種別')) else '',
                    'related_requirement_ids': str(row.get('関連要件ID', '')).strip() if pd.notna(row.get('関連要件ID')) else '',
                    'r1l_sr21cfts': str(row.get('(R1L_SR21CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR21CFTS)')) else '',
                    'r1l_sr22cfts': str(row.get('(R1L_SR22CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR22CFTS)')) else '',
                    'r1l_sr23cfts': str(row.get('(R1L_SR23CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR23CFTS)')) else '',
                    'r1l_sr24cfts': str(row.get('(R1L_SR24CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR24CFTS)')) else '',
                }

                data.append(record)

            return data, total_count

        except Exception as e:
            raise Exception(f"Error parsing {file_path.name}: {str(e)}")

    def import_to_database(self, data: List[Dict]) -> int:
        """
        Import data to database.

        Returns:
            Number of records successfully inserted
        """
        if not data:
            return 0

        db = SessionLocal()
        inserted_count = 0

        try:
            for item in data:
                try:
                    # Check if record already exists
                    existing = db.query(SYS2RequirementDB).filter(
                        SYS2RequirementDB.melco_id == item['melco_id']
                    ).first()

                    if existing:
                        # Update existing record
                        for key, value in item.items():
                            setattr(existing, key, value)
                    else:
                        # Insert new record
                        db_record = SYS2RequirementDB(**item)
                        db.add(db_record)
                        inserted_count += 1

                    db.commit()

                except Exception as e:
                    db.rollback()
                    print(f"  Error inserting {item.get('melco_id', 'unknown')}: {str(e)}")
                    continue

            return inserted_count

        finally:
            db.close()

    def process_all_files(self) -> Dict:
        """Process all SYS.2 Excel files in the folder."""
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)

        # Find all Excel files
        excel_files = self.find_excel_files()
        self.report['total_files'] = len(excel_files)

        if not excel_files:
            print(f"No SYS.2 Excel files found in {self.excel_folder}")
            return self.report

        print(f"Found {len(excel_files)} SYS.2 Excel files")
        print("-" * 80)

        # Process each file
        for idx, file_path in enumerate(excel_files, 1):
            cfts_id, cfts_name = self.extract_cfts_from_filename(file_path.name)
            print(f"\n[{idx}/{len(excel_files)}] Processing: {file_path.name}")
            print(f"  CFTS: {cfts_id} - {cfts_name}")

            try:
                # Parse Excel file
                data, total_count = self.parse_excel_file(file_path)
                print(f"  Total records: {total_count}")
                print(f"  Valid records: {len(data)}")

                # Import to database
                inserted_count = self.import_to_database(data)
                print(f"  Inserted: {inserted_count}")

                # Update report
                self.report['success_files'].append(file_path.name)
                self.report['total_records'] += total_count
                self.report['inserted_records'] += inserted_count
                self.report['skipped_records'] += (len(data) - inserted_count)

            except Exception as e:
                error_msg = str(e)
                print(f"  ERROR: {error_msg}")
                self.report['failed_files'].append(file_path.name)
                self.report['errors'].append({
                    'file': file_path.name,
                    'error': error_msg
                })

        return self.report

    def print_summary(self):
        """Print import summary report."""
        print("\n" + "=" * 80)
        print("SYS.2 IMPORT SUMMARY")
        print("=" * 80)
        print(f"Total files processed: {self.report['total_files']}")
        print(f"Successful: {len(self.report['success_files'])}")
        print(f"Failed: {len(self.report['failed_files'])}")
        print(f"\nTotal records read: {self.report['total_records']}")
        print(f"Successfully inserted: {self.report['inserted_records']}")
        print(f"Skipped (duplicates/updates): {self.report['skipped_records']}")

        # Verify database
        db = SessionLocal()
        try:
            total_in_db = db.query(SYS2RequirementDB).count()
            print(f"\nTotal SYS.2 records in database: {total_in_db}")
        finally:
            db.close()

        if self.report['failed_files']:
            print("\nFailed files:")
            for file in self.report['failed_files']:
                print(f"  - {file}")

        if self.report['errors']:
            print("\nErrors:")
            for err in self.report['errors']:
                print(f"  - {err['file']}: {err['error']}")

        print("=" * 80)

        # Save report to file
        report_file = f"sys2_import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed report saved to: {report_file}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python batch_import_sys2.py <sys2_excel_folder>")
        print("\nExample: python batch_import_sys2.py ../data/R1L_SYS.2")
        sys.exit(1)

    excel_folder = sys.argv[1]

    if not os.path.isdir(excel_folder):
        print(f"Error: {excel_folder} is not a valid directory")
        sys.exit(1)

    # Create importer and process files
    importer = SYS2Importer(excel_folder)
    importer.process_all_files()
    importer.print_summary()


if __name__ == "__main__":
    main()
