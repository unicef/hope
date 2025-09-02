import io
import re
from datetime import datetime
from typing import List, Tuple

from django.conf import settings

from hct_mis_api.apps.core.services.ftp_client import FTPClient


class WesternUnionFTPClient(FTPClient):
    HOST = getattr(settings, "WESTERN_UNION_FTP_SERVER", "")
    PORT = getattr(settings, "WESTERN_UNION_FTP_PORT", 22)
    USERNAME = getattr(settings, "WESTERN_UNION_FTP_USERNAME", "")
    PASSWORD = getattr(settings, "WESTERN_UNION_FTP_PASSWORD", "")

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
