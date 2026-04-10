from io import BufferedReader, BytesIO
from pathlib import Path
from typing import IO

from openpyxl.workbook.workbook import Workbook

def load_workbook(
    filename: str | Path | BufferedReader | BytesIO | IO[bytes],
    read_only: bool = ...,
    keep_vba: bool = ...,
    data_only: bool = ...,
    keep_links: bool = ...,
) -> Workbook: ...
