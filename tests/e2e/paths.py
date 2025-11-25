from pathlib import Path

from environ import Env

env = Env()
HERE = Path(__file__).resolve().parent

# Base dir for all e2e artefacts; relative to tests dir by default
OUTPUT_DATA_ROOT = Path(env("OUTPUT_DATA_ROOT", default=str(HERE / "output_data"))).resolve()

REPORT_DIRECTORY = OUTPUT_DATA_ROOT / "report"
DOWNLOAD_DIRECTORY = REPORT_DIRECTORY / "downloads"
SCREENSHOT_DIRECTORY = REPORT_DIRECTORY / "screenshot"
