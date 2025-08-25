import io
import os
import re
from datetime import datetime
from typing import List, Tuple

from hct_mis_api.apps.core.services.ftp_client import FTPClient


class WesternUnionFTPClient(FTPClient):
    HOST = os.getenv("FTP_WESTERN_UNION_SERVER", "")
    PORT = int(os.getenv("FTP_WESTERN_UNION_PORT", "22"))
    USERNAME = os.getenv("FTP_WESTERN_UNION_USERNAME", "")
    PASSWORD = os.getenv("FTP_WESTERN_UNION_PASSWORD", "")

    QCF_PREFIX_PATTERN = re.compile(r"^QCF-[A-Z0-9]+-[A-Z]+-\d{8}.*\.zip$", re.IGNORECASE)

    def print_files(self) -> None:
        files = self.list_files_w_attrs()
        for attr in files:
            print(
                {
                    "filename": attr.filename,
                    "modified": datetime.fromtimestamp(attr.st_mtime),
                }
            )

    def get_files_since(self, date_from: datetime) -> List[Tuple[str, io.BytesIO]]:
        files = [f for f in self.list_files_w_attrs() if datetime.fromtimestamp(f.st_mtime) >= date_from]
        return_files = []
        for f in files:
            filename = f.filename
            if self.QCF_PREFIX_PATTERN.match(filename):
                file_like = self.download(filename)
                return_files.append((filename, file_like))

        return return_files
