from datetime import datetime
import io
import re

from django.conf import settings

from hope.apps.core.services.ftp_client import FTPClient


class WesternUnionFTPClient(FTPClient):
    HOST = getattr(settings, "FTP_WESTERN_UNION_SERVER", "")
    PORT = getattr(settings, "FTP_WESTERN_UNION_PORT", 22)
    USERNAME = getattr(settings, "FTP_WESTERN_UNION_USERNAME", "")
    PASSWORD = getattr(settings, "FTP_WESTERN_UNION_PASSWORD", "")

    QCF_PREFIX_PATTERN = re.compile(r"^QCF-[A-Z0-9]+-[A-Z]+-\d{8}.*\.zip$", re.IGNORECASE)

    def print_files(self) -> None:
        files = self.list_files_w_attrs()
        for _attr in files:
            pass

    def get_files_since(self, date_from: datetime) -> list[tuple[str, io.BytesIO]]:
        files = [f for f in self.list_files_w_attrs() if datetime.fromtimestamp(f.st_mtime) >= date_from]
        return_files = []
        for f in files:
            filename = f.filename
            if self.QCF_PREFIX_PATTERN.match(filename):
                file_like = self.download(filename)
                return_files.append((filename, file_like))

        return return_files

    def get_files_by_name(self, name_substring: str) -> list[tuple[str, io.BytesIO]]:
        name_substring_lower = name_substring.lower()
        matched_files = []

        for f in self.list_files_w_attrs():
            if name_substring_lower in f.filename.lower():
                file_like = self.download(f.filename)
                matched_files.append((f.filename, file_like))

        return matched_files
