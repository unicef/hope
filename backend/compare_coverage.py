import sys
import xml.etree.ElementTree as ET

new_file_argument = sys.argv[1]
old_file_argument = sys.argv[2] if len(sys.argv) == 3 else None
if not new_file_argument:
    print("no new file argument, skipping coverage check")
    exit(0)


def get_coverage_from_report(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        coverage = float(root.get("line-rate"))
        return coverage
    except:
        return None


current_coverage = get_coverage_from_report(new_file_argument)
previous_coverage = 0
if old_file_argument:
    previous_coverage = get_coverage_from_report(old_file_argument)
if previous_coverage is None:
    print("could not get previous coverage, current coverage is", current_coverage)
    exit(0)
elif current_coverage - previous_coverage < 0:
    print(f"coverage decreased from {previous_coverage} to {current_coverage}")
    exit(1)
else:
    print("coverage ok")
    exit(0)
