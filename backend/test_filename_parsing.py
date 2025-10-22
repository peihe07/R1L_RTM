#!/usr/bin/env python3
"""Test filename parsing for both old and new formats."""
import re
from typing import Tuple


def extract_cfts_from_filename(filename: str) -> Tuple[str, str]:
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


def test_filenames():
    """Test filename parsing with various formats."""
    test_cases = [
        # New format (SYS1_CFTS)
        ("SYS1_CFTS041_Connected Services Management_SR26.xlsx", "CFTS041", "Connected Services Management"),
        ("SYS1_CFTS039_Naviagation_SR26.xlsx", "CFTS039", "Naviagation"),
        ("SYS1_CFTS016_Anti-Theft_SR26.xlsx", "CFTS016", "Anti-Theft"),

        # Old format (CFTS)
        ("CFTS016_Anti-Theft.xlsx", "CFTS016", "Anti-Theft"),
        ("CFTS041_Connected Services Management.xlsx", "CFTS041", "Connected Services Management"),
    ]

    print("Testing filename parsing:")
    print("=" * 80)

    all_passed = True
    for filename, expected_id, expected_name in test_cases:
        cfts_id, cfts_name = extract_cfts_from_filename(filename)
        passed = (cfts_id == expected_id and cfts_name == expected_name)

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status} {filename}")
        print(f"  Expected: {expected_id} - {expected_name}")
        print(f"  Got:      {cfts_id} - {cfts_name}")

        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")

    return all_passed


if __name__ == "__main__":
    import sys
    success = test_filenames()
    sys.exit(0 if success else 1)
