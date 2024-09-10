import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import Optional

new_file_argument = sys.argv[1]
old_file_argument = sys.argv[2] if len(sys.argv) == 3 else None
if not new_file_argument:
    print("no new file argument, skipping coverage check")
    exit(0)


def get_coverage_from_report(file_path: str) -> Optional[Decimal]:
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        lines_valid = Decimal(root.get("lines-valid"))  # type: ignore
        lines_covered = Decimal(root.get("lines-covered"))  # type: ignore
        coverage = lines_covered / lines_valid
        return coverage
    except (FileNotFoundError, IsADirectoryError):
        return None


current_coverage = get_coverage_from_report(new_file_argument)
previous_coverage: Optional[Decimal] = Decimal("0.0")
if old_file_argument:
    previous_coverage = get_coverage_from_report(old_file_argument)
if previous_coverage is None:
    print("could not get previous coverage, current coverage is", current_coverage)
    exit(0)
if current_coverage is None:
    print("could not get current coverage, previous coverage was", previous_coverage)
    exit(0)
elif current_coverage - previous_coverage < Decimal(0.0):
    print(f"coverage decreased from {previous_coverage} to {current_coverage}")
    exit(1)
else:
    print(f"coverage ok \nprevious coverage: {previous_coverage} \ncurrent coverage: {current_coverage}")
    exit(0)
