#!/usr/bin/env python3
"""Integrate SYS2 data with existing SYS1 data in database."""
import pandas as pd
import sys
from pathlib import Path
from typing import Dict, Tuple

from app.db.database import SessionLocal
from app.models.cfts_db import CFTSRequirementDB


class SYS2Integrator:
    """Integrate SYS2 Excel data with existing database records."""

    def __init__(self, excel_file: str, cfts_number: str):
        """
        Initialize SYS2 integrator.

        Args:
            excel_file: Path to SYS2 Excel file
            cfts_number: CFTS number (e.g., "CFTS021")
        """
        self.excel_file = Path(excel_file)
        self.cfts_number = cfts_number
        self.stats = {
            'total_rows': 0,
            'matched': 0,
            'updated': 0,
            'not_matched': 0,
            'errors': []
        }

    def parse_sys2_excel(self) -> Dict[str, Tuple[str, str]]:
        """
        Parse SYS2 Excel file and extract mapping data.

        Returns:
            Dict mapping req_id (E欄) to tuple of (melco_id (B欄), scope (I欄))
        """
        print(f"Reading SYS2 Excel file: {self.excel_file}")

        # Read Excel file, header is at row 4 (index 3)
        df = pd.read_excel(self.excel_file, header=3)

        print(f"Total rows in Excel: {len(df)}")

        # Column mapping (0-indexed):
        # B = index 1: Melco ID
        # E = index 4: Source Requirement ID (來源需求項目ID)
        # I = index 8: SW/HW/System (Scope)

        mapping = {}
        for idx, row in df.iterrows():
            # Get values from columns
            req_id_raw = row.iloc[4]  # E欄: Source Requirement ID
            melco_id_raw = row.iloc[1]  # B欄: Melco ID
            scope_raw = row.iloc[8]  # I欄: SW/HW/System

            # Skip header rows and empty rows
            if pd.isna(req_id_raw) or str(req_id_raw).strip() in ['', '來源需求項目ID \nSource Requirement items']:
                continue

            # Convert req_id to string (it's a number in Excel)
            req_id = str(int(req_id_raw)) if isinstance(req_id_raw, (int, float)) else str(req_id_raw).strip()

            # Get melco_id and scope
            melco_id = str(melco_id_raw).strip() if pd.notna(melco_id_raw) else ''
            scope = str(scope_raw).strip() if pd.notna(scope_raw) else ''

            # Store mapping
            if req_id:
                mapping[req_id] = (melco_id, scope)
                self.stats['total_rows'] += 1

        print(f"Extracted {len(mapping)} valid mappings from SYS2 Excel")
        return mapping

    def update_database(self, mapping: Dict[str, Tuple[str, str]]) -> None:
        """
        Update database records with SYS2 data.

        Args:
            mapping: Dict mapping req_id to (melco_id, scope)
        """
        db = SessionLocal()
        try:
            print(f"\nUpdating database for CFTS: {self.cfts_number}")

            # Get all records for this CFTS
            records = db.query(CFTSRequirementDB).filter(
                CFTSRequirementDB.cfts_id == self.cfts_number
            ).all()

            print(f"Found {len(records)} records in database for {self.cfts_number}")

            for record in records:
                req_id = record.req_id.strip()

                if req_id in mapping:
                    melco_id, scope = mapping[req_id]

                    # Update record
                    record.melco_id = melco_id
                    record.sys2_scope = scope

                    self.stats['matched'] += 1
                    print(f"  ✓ Matched req_id={req_id}: melco_id={melco_id}, scope={scope}")
                else:
                    self.stats['not_matched'] += 1
                    print(f"  ✗ No match for req_id={req_id}")

            # Commit changes
            db.commit()
            self.stats['updated'] = self.stats['matched']
            print(f"\nCommitted {self.stats['updated']} updates to database")

        except Exception as e:
            db.rollback()
            error_msg = f"Error updating database: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.stats['errors'].append(error_msg)
            raise
        finally:
            db.close()

    def integrate(self) -> Dict:
        """
        Run the integration process.

        Returns:
            Statistics dictionary
        """
        try:
            # Parse SYS2 Excel
            mapping = self.parse_sys2_excel()

            if not mapping:
                print("No valid data found in SYS2 Excel file")
                return self.stats

            # Update database
            self.update_database(mapping)

        except Exception as e:
            error_msg = f"Integration failed: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.stats['errors'].append(error_msg)

        return self.stats

    def print_summary(self):
        """Print integration summary."""
        print("\n" + "=" * 80)
        print("SYS2 INTEGRATION SUMMARY")
        print("=" * 80)
        print(f"CFTS Number: {self.cfts_number}")
        print(f"Excel File: {self.excel_file.name}")
        print(f"\nTotal SYS2 rows: {self.stats['total_rows']}")
        print(f"Matched records: {self.stats['matched']}")
        print(f"Updated records: {self.stats['updated']}")
        print(f"Not matched: {self.stats['not_matched']}")

        if self.stats['errors']:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"  - {error}")

        print("=" * 80)


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python integrate_sys2.py <sys2_excel_file> <cfts_number>")
        print("\nExample:")
        print("  python integrate_sys2.py data/cfts_excel/SYS2/SYS2_CFTS021.xlsx CFTS021")
        sys.exit(1)

    excel_file = sys.argv[1]
    cfts_number = sys.argv[2]

    if not Path(excel_file).exists():
        print(f"Error: Excel file not found: {excel_file}")
        sys.exit(1)

    # Create integrator and run
    integrator = SYS2Integrator(excel_file, cfts_number)
    integrator.integrate()
    integrator.print_summary()


if __name__ == "__main__":
    main()
