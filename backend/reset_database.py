#!/usr/bin/env python3
"""
Reset and recreate database tables for R1L_RTM.

This script will:
1. Drop all existing tables
2. Recreate tables with current schema
3. Ensure clean state for fresh data import
"""
import sys
from sqlalchemy import text

from app.db.database import engine, Base, SessionLocal
from app.models.cfts_db import CFTSRequirementDB
from app.models.sys2_requirement import SYS2RequirementDB
from app.models.testcase import TestCaseDB


def confirm_reset():
    """Ask user for confirmation before proceeding."""
    print("=" * 80)
    print("⚠️  DATABASE RESET WARNING")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. DROP all existing data in the following tables:")
    print("     - cfts_requirements")
    print("     - sys2_requirements")
    print("     - testcases")
    print("  2. RECREATE tables with current schema")
    print("\n⚠️  ALL EXISTING DATA WILL BE PERMANENTLY DELETED!")
    print("\n" + "=" * 80)

    response = input("\nAre you sure you want to continue? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled.")
        return False

    # Double confirmation
    print("\n⚠️  Last chance to cancel!")
    response2 = input("Type 'DELETE ALL DATA' to confirm: ").strip()

    if response2 != 'DELETE ALL DATA':
        print("\n❌ Operation cancelled.")
        return False

    return True


def get_table_counts():
    """Get current record counts from all tables."""
    db = SessionLocal()
    try:
        cfts_count = db.query(CFTSRequirementDB).count()
        sys2_count = db.query(SYS2RequirementDB).count()
        testcase_count = db.query(TestCaseDB).count()
        return cfts_count, sys2_count, testcase_count
    except Exception as e:
        print(f"Note: Could not get table counts (tables may not exist yet): {e}")
        return 0, 0, 0
    finally:
        db.close()


def drop_all_tables():
    """Drop all tables."""
    print("\n🗑️  Dropping existing tables...")

    try:
        # Drop tables in reverse order of dependencies
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False


def create_all_tables():
    """Create all tables with current schema."""
    print("\n🔨 Creating tables with current schema...")

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")

        # Verify tables were created
        db = SessionLocal()
        try:
            # Test each table
            db.query(CFTSRequirementDB).count()
            print("  ✓ cfts_requirements table created")

            db.query(SYS2RequirementDB).count()
            print("  ✓ sys2_requirements table created")

            db.query(TestCaseDB).count()
            print("  ✓ testcases table created")

        finally:
            db.close()

        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def print_summary(before_counts, success):
    """Print summary of the reset operation."""
    cfts_before, sys2_before, testcase_before = before_counts

    print("\n" + "=" * 80)
    print("DATABASE RESET SUMMARY")
    print("=" * 80)

    if success:
        print("\n✅ Database reset completed successfully!\n")
        print("Records deleted:")
        print(f"  - CFTS Requirements:  {cfts_before:,}")
        print(f"  - SYS.2 Requirements: {sys2_before:,}")
        print(f"  - TestCases:          {testcase_before:,}")
        print(f"\n  Total deleted:        {cfts_before + sys2_before + testcase_before:,}")

        print("\n📋 Database is now ready for fresh data import.")
        print("\nNext steps:")
        print("  1. Import CFTS data:")
        print("     python batch_import_cfts_new.py ../data/CFTS")
        print("\n  2. Import SYS.2 data:")
        print("     python batch_import_sys2.py ../data/R1L_SYS.2.xlsx")
        print("\n  3. Import TestCase data:")
        print("     python batch_import_testcase.py ../data/R1L_TestCase.xlsx")
    else:
        print("\n❌ Database reset failed!")
        print("\nPlease check the error messages above and try again.")

    print("=" * 80)


def main():
    """Main function."""
    # Check for --force flag
    force_reset = '--force' in sys.argv or '-f' in sys.argv

    print("\n" + "=" * 80)
    print("R1L_RTM Database Reset Tool")
    print("=" * 80)

    # Get current counts
    print("\n📊 Current database status:")
    before_counts = get_table_counts()
    cfts_count, sys2_count, testcase_count = before_counts

    if cfts_count > 0 or sys2_count > 0 or testcase_count > 0:
        print(f"  - CFTS Requirements:  {cfts_count:,} records")
        print(f"  - SYS.2 Requirements: {sys2_count:,} records")
        print(f"  - TestCases:          {testcase_count:,} records")
        print(f"\n  Total:                {cfts_count + sys2_count + testcase_count:,} records")
    else:
        print("  - Database is empty or tables do not exist yet")

    # Get confirmation (skip if --force flag is used)
    if force_reset:
        print("\n⚠️  --force flag detected, skipping confirmation")
    else:
        if not confirm_reset():
            sys.exit(0)

    # Perform reset
    print("\n" + "=" * 80)
    print("🚀 Starting database reset...")
    print("=" * 80)

    # Drop tables
    if not drop_all_tables():
        print_summary(before_counts, False)
        sys.exit(1)

    # Create tables
    if not create_all_tables():
        print_summary(before_counts, False)
        sys.exit(1)

    # Print summary
    print_summary(before_counts, True)


if __name__ == "__main__":
    main()
