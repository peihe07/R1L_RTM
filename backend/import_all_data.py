#!/usr/bin/env python3
"""
Import all R1L_RTM data in correct order.

This script will:
1. Import CFTS data from data/CFTS folder
2. Import SYS.2 data from data/R1L_SYS.2.xlsx
3. Import TestCase data from data/R1L_TestCase.xlsx
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Import the individual importers
from batch_import_cfts_new import CFTSImporter
from batch_import_sys2 import SYS2Importer
from batch_import_testcase import TestCaseImporter


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def validate_data_files():
    """Validate that all required data files exist."""
    print_header("📋 Validating Data Files")

    base_path = Path(__file__).parent.parent / "data"
    cfts_folder = base_path / "CFTS"
    sys2_file = base_path / "R1L_SYS.2.xlsx"
    testcase_file = base_path / "R1L_TestCase.xlsx"

    errors = []

    # Check CFTS folder
    if not cfts_folder.exists():
        errors.append(f"❌ CFTS folder not found: {cfts_folder}")
    else:
        cfts_files = list(cfts_folder.glob("*.xlsx"))
        if not cfts_files:
            errors.append(f"❌ No Excel files found in CFTS folder: {cfts_folder}")
        else:
            print(f"✅ CFTS folder: {cfts_folder}")
            print(f"   Found {len(cfts_files)} Excel files")

    # Check SYS.2 file
    if not sys2_file.exists():
        errors.append(f"❌ SYS.2 file not found: {sys2_file}")
    else:
        print(f"✅ SYS.2 file: {sys2_file}")
        print(f"   Size: {sys2_file.stat().st_size:,} bytes")

    # Check TestCase file
    if not testcase_file.exists():
        errors.append(f"❌ TestCase file not found: {testcase_file}")
    else:
        print(f"✅ TestCase file: {testcase_file}")
        print(f"   Size: {testcase_file.stat().st_size:,} bytes")

    if errors:
        print("\n" + "=" * 80)
        print("❌ VALIDATION FAILED")
        print("=" * 80)
        for error in errors:
            print(error)
        return False

    print("\n✅ All data files validated successfully!")
    return True


def import_cfts_data():
    """Import CFTS data."""
    print_header("1️⃣  Importing CFTS Data")

    cfts_folder = Path(__file__).parent.parent / "data" / "CFTS"

    try:
        importer = CFTSImporter(str(cfts_folder))
        importer.process_all_files()
        importer.print_summary()
        return True
    except Exception as e:
        print(f"\n❌ CFTS import failed: {e}")
        return False


def import_sys2_data():
    """Import SYS.2 data."""
    print_header("2️⃣  Importing SYS.2 Data")

    sys2_file = Path(__file__).parent.parent / "data" / "R1L_SYS.2.xlsx"

    try:
        importer = SYS2Importer(str(sys2_file))
        importer.process_file()
        importer.print_summary()
        return True
    except Exception as e:
        print(f"\n❌ SYS.2 import failed: {e}")
        return False


def import_testcase_data():
    """Import TestCase data."""
    print_header("3️⃣  Importing TestCase Data")

    testcase_file = Path(__file__).parent.parent / "data" / "R1L_TestCase.xlsx"

    try:
        importer = TestCaseImporter(str(testcase_file))
        importer.process_file()
        importer.print_summary()
        return True
    except Exception as e:
        print(f"\n❌ TestCase import failed: {e}")
        return False


def print_final_summary(start_time, cfts_success, sys2_success, testcase_success):
    """Print final summary of all imports."""
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 80)
    print("📊 FINAL IMPORT SUMMARY")
    print("=" * 80)

    print("\nImport Results:")
    print(f"  1. CFTS Data:     {'✅ SUCCESS' if cfts_success else '❌ FAILED'}")
    print(f"  2. SYS.2 Data:    {'✅ SUCCESS' if sys2_success else '❌ FAILED'}")
    print(f"  3. TestCase Data: {'✅ SUCCESS' if testcase_success else '❌ FAILED'}")

    all_success = cfts_success and sys2_success and testcase_success

    print(f"\nOverall Status: {'✅ ALL IMPORTS SUCCESSFUL' if all_success else '⚠️  SOME IMPORTS FAILED'}")
    print(f"Total Duration: {duration.total_seconds():.2f} seconds")

    if all_success:
        print("\n🎉 All data has been successfully imported!")
        print("\n📋 Next steps:")
        print("  1. Start the backend server:")
        print("     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n  2. Check API documentation:")
        print("     http://localhost:8000/docs")
        print("\n  3. Start the frontend (in another terminal):")
        print("     cd ../frontend && npm run dev")
    else:
        print("\n⚠️  Please check the error messages above and fix any issues.")
        print("   You may need to:")
        print("   - Check database connection")
        print("   - Verify data file formats")
        print("   - Check for missing dependencies")

    print("=" * 80)


def main():
    """Main function."""
    # Check for --force flag
    force_import = '--force' in sys.argv or '-f' in sys.argv

    start_time = datetime.now()

    print("\n" + "=" * 80)
    print("🚀 R1L_RTM Complete Data Import")
    print("=" * 80)
    print(f"\nStart time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Validate data files
    if not validate_data_files():
        sys.exit(1)

    # Confirm before proceeding (skip if --force flag is used)
    if force_import:
        print("\n⚠️  --force flag detected, skipping confirmation")
    else:
        print("\n" + "=" * 80)
        response = input("\n▶️  Ready to import all data. Continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n❌ Import cancelled.")
            sys.exit(0)

    # Import data in order
    cfts_success = import_cfts_data()
    sys2_success = import_sys2_data()
    testcase_success = import_testcase_data()

    # Print final summary
    print_final_summary(start_time, cfts_success, sys2_success, testcase_success)

    # Exit with appropriate code
    sys.exit(0 if (cfts_success and sys2_success and testcase_success) else 1)


if __name__ == "__main__":
    main()
