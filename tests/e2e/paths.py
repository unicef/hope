from pathlib import Path

HERE = Path(__file__).resolve().parent
E2E_ROOT = HERE.parent

# Local build directory in the project root
OUTPUT_DATA_ROOT = E2E_ROOT / "output_data"
OUTPUT_DATA_ROOT.mkdir(exist_ok=True)

REPORT_DIRECTORY = OUTPUT_DATA_ROOT / "report"
REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)

DOWNLOAD_DIRECTORY = REPORT_DIRECTORY / "downloads"
DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

SCREENSHOT_DIRECTORY = REPORT_DIRECTORY / "screenshot"
SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
