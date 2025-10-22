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
    """Import SYS.2 Excel file."""

    def __init__(self, excel_file: str):
        """
        Initialize SYS.2 importer.

        Args:
            excel_file: Path to R1L_SYS.2.xlsx file
        """
        self.excel_file = Path(excel_file)
        self.report = {
            'total_records': 0,
            'inserted_records': 0,
            'skipped_records': 0,
            'errors': []
        }

    def parse_excel_file(self) -> List[Dict]:
        """
        Parse R1L_SYS.2.xlsx file.

        Returns:
            List of parsed data records
        """
        try:
            # Read Excel file
            df = pd.read_excel(self.excel_file)
            self.report['total_records'] = len(df)

            # Convert to list of dicts
            data = []
            for _, row in df.iterrows():
                # Get Melco ID - support both English and Japanese column names
                melco_id = row.get('Melco Id', row.get('要件ID', ''))
                melco_id = str(melco_id).strip() if pd.notna(melco_id) else ''
                if not melco_id or melco_id == 'nan':
                    continue  # Skip rows without Melco ID

                # Extract CFTS ID from Melco ID (e.g., PSCFTS069-1-2-1 -> CFTS069)
                cfts_match = re.search(r'CFTS\d+', melco_id)
                cfts_id = cfts_match.group(0) if cfts_match else ''

                # Extract all fields - support both English and Japanese column names
                record = {
                    'melco_id': melco_id,
                    'cfts_id': cfts_id,
                    'cfts_name': '',  # Will be populated later from CFTS data
                    'requirement_en': str(row.get('Requirement', row.get('要件(英語)', ''))).strip() if pd.notna(row.get('Requirement', row.get('要件(英語)'))) else '',
                    'reason_en': str(row.get('Reason', row.get('理由(英語)', ''))).strip() if pd.notna(row.get('Reason', row.get('理由(英語)'))) else '',
                    'supplement_en': str(row.get('Supplementary', row.get('補足(英語)', ''))).strip() if pd.notna(row.get('Supplementary', row.get('補足(英語)'))) else '',
                    'confirmation_phase': str(row.get('Verification Phase', row.get('確認フェーズ', ''))).strip() if pd.notna(row.get('Verification Phase', row.get('確認フェーズ'))) else '',
                    'verification_criteria': str(row.get('Verification Criteria', row.get('検証基準', ''))).strip() if pd.notna(row.get('Verification Criteria', row.get('検証基準'))) else '',
                    'type': str(row.get('Type', row.get('種別', ''))).strip() if pd.notna(row.get('Type', row.get('種別'))) else '',
                    'related_requirement_ids': str(row.get('Related Requirement ID', row.get('関連要件ID', ''))).strip() if pd.notna(row.get('Related Requirement ID', row.get('関連要件ID'))) else '',
                    'r1l_sr21cfts': str(row.get('(R1L_SR21CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR21CFTS)')) else '',
                    'r1l_sr22cfts': str(row.get('(R1L_SR22CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR22CFTS)')) else '',
                    'r1l_sr23cfts': str(row.get('(R1L_SR23CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR23CFTS)')) else '',
                    'r1l_sr24cfts': str(row.get('(R1L_SR24CFTS)', '')).strip() if pd.notna(row.get('(R1L_SR24CFTS)')) else '',
                }

                data.append(record)

            return data

        except Exception as e:
            raise Exception(f"Error parsing {self.excel_file.name}: {str(e)}")

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

    def process_file(self) -> Dict:
        """Process R1L_SYS.2.xlsx file."""
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)

        print(f"Processing: {self.excel_file.name}")
        print("-" * 80)

        try:
            # Parse Excel file
            data = self.parse_excel_file()
            print(f"  Total records: {self.report['total_records']}")
            print(f"  Valid records: {len(data)}")

            # Import to database
            inserted_count = self.import_to_database(data)
            print(f"  Inserted: {inserted_count}")

            # Update report
            self.report['inserted_records'] = inserted_count
            self.report['skipped_records'] = len(data) - inserted_count

        except Exception as e:
            error_msg = str(e)
            print(f"  ERROR: {error_msg}")
            self.report['errors'].append({
                'file': self.excel_file.name,
                'error': error_msg
            })

        return self.report

    def print_summary(self):
        """Print import summary report."""
        print("\n" + "=" * 80)
        print("SYS.2 IMPORT SUMMARY")
        print("=" * 80)
        print(f"Total records read: {self.report['total_records']}")
        print(f"Successfully inserted: {self.report['inserted_records']}")
        print(f"Skipped (duplicates/updates): {self.report['skipped_records']}")

        # Verify database
        db = SessionLocal()
        try:
            total_in_db = db.query(SYS2RequirementDB).count()
            print(f"\nTotal SYS.2 records in database: {total_in_db}")

            # Show sample record
            sample = db.query(SYS2RequirementDB).first()
            if sample:
                print(f"\nSample record:")
                print(f"  Melco ID: {sample.melco_id}")
                print(f"  CFTS ID: {sample.cfts_id}")
                print(f"  Requirement: {sample.requirement_en[:100]}...")
        finally:
            db.close()

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
        print("Usage: python batch_import_sys2.py <sys2_excel_file>")
        print("\nExample: python batch_import_sys2.py ../data/R1L_SYS.2.xlsx")
        sys.exit(1)

    excel_file = sys.argv[1]

    if not os.path.isfile(excel_file):
        print(f"Error: {excel_file} is not a valid file")
        sys.exit(1)

    # Create importer and process file
    importer = SYS2Importer(excel_file)
    importer.process_file()
    importer.print_summary()


if __name__ == "__main__":
    main()
