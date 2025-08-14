# ftp/base.py

import io
import logging

import paramiko

logger = logging.getLogger(__name__)


class FTPClient:
    HOST: str = ""
    PORT: int = 22  # default SFTP port
    USERNAME: str = ""
    PASSWORD: str = ""

    def __init__(self) -> None:
        if not all([self.HOST, self.PORT, self.USERNAME, self.PASSWORD]):
            raise ValueError("FTP credentials (HOST, PORT, USERNAME, PASSWORD) must be defined on the class")

        self._transport = paramiko.Transport((self.HOST, self.PORT))
        self._transport.connect(username=self.USERNAME, password=self.PASSWORD)
        self.client = paramiko.SFTPClient.from_transport(self._transport)

    def disconnect(self) -> None:
        if self.client:
            self.client.close()
        if self._transport:
            self._transport.close()

    def list_files(self, path: str = ".") -> list:
        return self.client.listdir(path)

    def list_files_w_attrs(self, path: str = ".") -> list:
        return self.client.listdir_attr(path)

    def get(self, remote_path: str, local_path: str) -> None:
        try:
            self.client.get(remote_path, local_path)
        except FileNotFoundError:
            logger.info(f"File: {remote_path} was not found on the source server")

    def download(self, remote_path: str) -> io.BytesIO:
        fl = io.BytesIO()
        self.client.getfo(remote_path, fl)
        fl.seek(0)
        return fl
