#!/usr/bin/env python3
"""Import CFTS data from data/CFTS folder."""
import pandas as pd
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

from app.db.database import engine, SessionLocal, Base
from app.models.requirement import CFTSRequirement
from app.models.cfts_db import CFTSRequirementDB


class CFTSImporter:
    """Import CFTS Excel files from data/CFTS folder."""

    def __init__(self, excel_folder: str):
        """
        Initialize CFTS importer.

        Args:
            excel_folder: Path to folder containing CFTS Excel files
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
        """Find all CFTS Excel files in the folder."""
        excel_files = []
        for ext in ['.xlsx', '.xls']:
            for file in self.excel_folder.iterdir():
                # Support both formats: CFTS* and SYS1_CFTS*
                if (file.name.startswith('CFTS') or file.name.startswith('SYS1_CFTS')) and file.name.endswith(ext):
                    excel_files.append(file)
        return sorted(excel_files)

    def extract_cfts_from_filename(self, filename: str) -> Tuple[str, str]:
        """
        Extract CFTS number and name from filename.

        Example:
            CFTS016_Anti-Theft.xlsx -> (CFTS016, Anti-Theft)
            SYS1_CFTS016_Anti-Theft_SR26.xlsx -> (CFTS016, Anti-Theft)
        """
        # Extract CFTS number
        cfts_match = re.search(r'CFTS\d+', filename)
        cfts_id = cfts_match.group(0) if cfts_match else ''

        # Extract CFTS name (between CFTS number and _SR26 or .xlsx)
        # Handle both underscore and space
        # Pattern matches: CFTS\d+[_\s]description[_\s](SR\d+)?.xlsx
        name_match = re.search(r'CFTS\d+[_\s](.+?)(?:_SR\d+)?\.(xlsx|xls)', filename)
        cfts_name = name_match.group(1).strip() if name_match else ''

        return cfts_id, cfts_name

    def parse_excel_file(self, file_path: Path) -> Tuple[List[Dict], int]:
        """
        Parse a single CFTS Excel file.

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
                # Get ReqIF.ForeignID as req_id
                reqif_id = row.get('ReqIF.ForeignID', '')
                req_id = str(reqif_id).strip() if pd.notna(reqif_id) else ''

                # Get Source Id
                src_id = row.get('Source Id', '')
                source_id = str(src_id).strip() if pd.notna(src_id) else ''

                # Get Melco Id (keep as-is, don't split)
                melco_id_raw = row.get('Melco Id', '')
                melco_id = str(melco_id_raw).strip() if pd.notna(melco_id_raw) else ''

                # Get descriptions (SR26 and SR24)
                sr26_desc = row.get('SR26 Description', '')
                sr24_desc = row.get('SR24 Description', '')
                description = str(sr26_desc).strip() if pd.notna(sr26_desc) else ''
                sr24_description = str(sr24_desc).strip() if pd.notna(sr24_desc) else ''

                # Skip empty records (at least need req_id)
                if not req_id:
                    continue

                # Create record (keep Melco ID as-is with newlines)
                record = {
                    'cfts_id': cfts_id,
                    'cfts_name': cfts_name,
                    'req_id': req_id,
                    'source_id': source_id,
                    'description': description,
                    'sr24_description': sr24_description,
                    'melco_id': melco_id
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
                    # Check if record already exists by req_id
                    existing = db.query(CFTSRequirementDB).filter(
                        CFTSRequirementDB.req_id == item['req_id']
                    ).first()

                    if existing:
                        # Update existing record
                        for key, value in item.items():
                            setattr(existing, key, value)
                    else:
                        # Insert new record
                        db_record = CFTSRequirementDB(**item)
                        db.add(db_record)
                        inserted_count += 1

                    db.commit()

                except Exception as e:
                    db.rollback()
                    print(f"  Error inserting record: {str(e)}")
                    continue

            return inserted_count

        finally:
            db.close()

    def process_all_files(self) -> Dict:
        """Process all CFTS Excel files in the folder."""
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)

        # Find all Excel files
        excel_files = self.find_excel_files()
        self.report['total_files'] = len(excel_files)

        if not excel_files:
            print(f"No CFTS Excel files found in {self.excel_folder}")
            return self.report

        print(f"Found {len(excel_files)} CFTS Excel files")
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
        print("CFTS IMPORT SUMMARY")
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
            total_in_db = db.query(CFTSRequirementDB).count()
            print(f"\nTotal CFTS records in database: {total_in_db}")

            # Show sample with Melco ID
            sample = db.query(CFTSRequirementDB).filter(
                CFTSRequirementDB.melco_id != '',
                CFTSRequirementDB.melco_id != None
            ).first()
            if sample:
                print(f"\nSample record with Melco ID:")
                print(f"  CFTS: {sample.cfts_id} - {sample.cfts_name}")
                print(f"  Melco ID: {sample.melco_id}")
                print(f"  Req ID: {sample.req_id}")
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
        report_file = f"cfts_import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed report saved to: {report_file}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python batch_import_cfts_new.py <cfts_excel_folder>")
        print("\nExample: python batch_import_cfts_new.py ../data/CFTS")
        sys.exit(1)

    excel_folder = sys.argv[1]

    if not os.path.isdir(excel_folder):
        print(f"Error: {excel_folder} is not a valid directory")
        sys.exit(1)

    # Create importer and process files
    importer = CFTSImporter(excel_folder)
    importer.process_all_files()
    importer.print_summary()


if __name__ == "__main__":
    main()
