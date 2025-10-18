#!/usr/bin/env python3
"""Import TestCase data from R1L_TestCase.xlsx."""
import pandas as pd
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from app.db.database import engine, SessionLocal, Base
from app.models.testcase import TestCaseDB, TestCase


class TestCaseImporter:
    """Import TestCase from R1L_TestCase.xlsx."""

    def __init__(self, excel_file: str):
        """
        Initialize TestCase importer.

        Args:
            excel_file: Path to R1L_TestCase.xlsx file
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
        Parse R1L_TestCase.xlsx file.

        Returns:
            List of parsed test case records
        """
        try:
            # Read Excel file
            df = pd.read_excel(self.excel_file)
            self.report['total_records'] = len(df)

            # Convert to list of dicts
            data = []
            for idx, row in df.iterrows():
                # Get Feature ID (G欄) - 對應Melco ID
                feature_id = row.get('Feature-ID', '')
                feature_id = str(feature_id).strip() if pd.notna(feature_id) else ''

                # Skip rows without Feature ID
                if not feature_id:
                    continue

                # Extract A-F columns
                record = {
                    'feature_id': feature_id,
                    'source': str(row.get('Source', '')).strip() if pd.notna(row.get('Source')) else '',
                    'title': str(row.get('Title', '')).strip() if pd.notna(row.get('Title')) else '',
                    'section': str(row.get('Section', '')).strip() if pd.notna(row.get('Section')) else '',
                    'test_item_en': str(row.get('TestItem(EN)', '')).strip() if pd.notna(row.get('TestItem(EN)')) else '',
                    'precondition_procedure_jp': str(row.get('Precondition/Procedure(JP)', '')).strip() if pd.notna(row.get('Precondition/Procedure(JP)')) else '',
                    'criteria_jp': str(row.get('Criteria(JP)', '')).strip() if pd.notna(row.get('Criteria(JP)')) else '',
                    # Other columns
                    'mp': str(row.get('MP', '')).strip() if pd.notna(row.get('MP')) else '',
                    'ds': str(row.get('DS', '')).strip() if pd.notna(row.get('DS')) else '',
                    'dt': str(row.get('DT', '')).strip() if pd.notna(row.get('DT')) else '',
                    'hdcc': str(row.get('HDCC', '')).strip() if pd.notna(row.get('HDCC')) else '',
                    'ru': str(row.get('RU', '')).strip() if pd.notna(row.get('RU')) else '',
                    'specification': str(row.get('Specification', '')).strip() if pd.notna(row.get('Specification')) else '',
                    'priority': str(row.get('Priority', '')).strip() if pd.notna(row.get('Priority')) else '',
                    'test_version': str(row.get('Test Version', '')).strip() if pd.notna(row.get('Test Version')) else '',
                    'test_result': str(row.get('Test Result', '')).strip() if pd.notna(row.get('Test Result')) else '',
                    'tester': str(row.get('Tester', '')).strip() if pd.notna(row.get('Tester')) else '',
                    'issue_id': str(row.get('Issue ID', '')).strip() if pd.notna(row.get('Issue ID')) else '',
                    'note': str(row.get('Note', '')).strip() if pd.notna(row.get('Note')) else '',
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
                    # Insert new record (allow duplicates for same feature_id)
                    db_record = TestCaseDB(**item)
                    db.add(db_record)
                    inserted_count += 1
                    db.commit()

                except Exception as e:
                    db.rollback()
                    print(f"  Error inserting TestCase {item.get('title', 'unknown')}: {str(e)}")
                    self.report['errors'].append({
                        'title': item.get('title', 'unknown'),
                        'error': str(e)
                    })
                    continue

            return inserted_count

        finally:
            db.close()

    def process_file(self) -> Dict:
        """Process R1L_TestCase.xlsx file."""
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)

        print(f"Processing: {self.excel_file.name}")
        print("-" * 80)

        try:
            # Parse Excel file
            data = self.parse_excel_file()
            print(f"Total records: {self.report['total_records']}")
            print(f"Valid records with Feature ID: {len(data)}")

            # Import to database
            inserted_count = self.import_to_database(data)
            print(f"Inserted: {inserted_count}")

            self.report['inserted_records'] = inserted_count
            self.report['skipped_records'] = len(data) - inserted_count

        except Exception as e:
            error_msg = str(e)
            print(f"ERROR: {error_msg}")
            self.report['errors'].append({
                'file': self.excel_file.name,
                'error': error_msg
            })

        return self.report

    def print_summary(self):
        """Print import summary report."""
        print("\n" + "=" * 80)
        print("TESTCASE IMPORT SUMMARY")
        print("=" * 80)
        print(f"Total records read: {self.report['total_records']}")
        print(f"Successfully inserted: {self.report['inserted_records']}")
        print(f"Skipped/Errors: {self.report['skipped_records']}")

        # Verify database
        db = SessionLocal()
        try:
            total_in_db = db.query(TestCaseDB).count()
            print(f"\nTotal TestCase records in database: {total_in_db}")

            # Show sample
            sample = db.query(TestCaseDB).first()
            if sample:
                print(f"\nSample TestCase record:")
                print(f"  Feature ID: {sample.feature_id}")
                print(f"  Source: {sample.source}")
                print(f"  Title: {sample.title}")
                print(f"  Test Item: {sample.test_item_en[:100]}...")
        finally:
            db.close()

        if self.report['errors']:
            print(f"\nTotal errors: {len(self.report['errors'])}")
            print("First 5 errors:")
            for err in self.report['errors'][:5]:
                print(f"  - {err}")

        print("=" * 80)

        # Save report to file
        report_file = f"testcase_import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed report saved to: {report_file}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python batch_import_testcase.py <testcase_excel_file>")
        print("\nExample: python batch_import_testcase.py ../data/R1L_TestCase.xlsx")
        sys.exit(1)

    excel_file = sys.argv[1]

    if not os.path.isfile(excel_file):
        print(f"Error: {excel_file} is not a valid file")
        sys.exit(1)

    # Create importer and process file
    importer = TestCaseImporter(excel_file)
    importer.process_file()
    importer.print_summary()


if __name__ == "__main__":
    main()
