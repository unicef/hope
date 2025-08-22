import io
from datetime import datetime, timedelta
from typing import Any, Generator
from unittest import mock
from unittest.mock import MagicMock, patch

from django.test import TestCase

import pytest

from hct_mis_api.apps.payment.services.western_union_ftp import WesternUnionFTPClient


class WesternUnionFTPClientMock(WesternUnionFTPClient):
    HOST = "fakehost"
    PORT = 22
    USERNAME = "user"
    PASSWORD = "pass"


class WesternUnionFTPClientMockNoCredentials(WesternUnionFTPClient):
    HOST = ""
    PORT = 22
    USERNAME = "user"
    PASSWORD = "pass"


@pytest.fixture(autouse=True)
def mock_sftp() -> Generator[dict[str, Any], None, None]:
    mock_transport: MagicMock = MagicMock()
    mock_sftp_client: MagicMock = MagicMock()

    with patch(
        "hct_mis_api.apps.core.services.ftp_client.paramiko.Transport",
        return_value=mock_transport,
    ) as mock_transport_cls, patch(
        "hct_mis_api.apps.core.services.ftp_client.paramiko.SFTPClient.from_transport",
        return_value=mock_sftp_client,
    ) as mock_sftp_cls:
        yield {
            "transport_cls": mock_transport_cls,
            "sftp_cls": mock_sftp_cls,
            "transport": mock_transport,
            "sftp": mock_sftp_client,
        }


class TestWesternUnionFTPClient(TestCase):
    def make_attr(self, filename: str, modified_time: datetime) -> MagicMock:
        """Helper to build a fake SFTPAttributes-like object."""
        attr = mock.MagicMock()
        attr.filename = filename
        attr.st_mtime = modified_time.timestamp()
        return attr

    def test_print_files(
        self,
    ) -> None:
        ftp_client = WesternUnionFTPClientMock()
        ftp_client.client.listdir_attr = MagicMock(return_value=[])
        ftp_client.print_files()
        ftp_client.client.listdir_attr.assert_called_once()

    def test_get_files_since_filters_and_downloads(self) -> None:
        ftp_client = WesternUnionFTPClientMock()
        now = datetime.now()
        old_time = now - timedelta(days=5)
        new_time = now - timedelta(hours=1)

        # Prepare fake files
        attrs = [
            self.make_attr("QCF-123-XYZ-20250101.zip", new_time),  # valid + recent
            self.make_attr("not-matching.zip", new_time),  # wrong pattern
            self.make_attr("QCF-999-ABC-20240101.zip", old_time),  # too old
        ]

        with mock.patch.object(ftp_client, "list_files_w_attrs", return_value=attrs), mock.patch.object(
            ftp_client, "download", return_value=io.BytesIO(b"fake content")
        ) as mock_download:
            results = ftp_client.get_files_since(now - timedelta(days=1))

            self.assertEqual(len(results), 1)
            fname, filelike = results[0]
            self.assertEqual(fname, "QCF-123-XYZ-20250101.zip")
            self.assertIsInstance(filelike, io.BytesIO)
            self.assertEqual(filelike.getvalue(), b"fake content")

            mock_download.assert_called_once_with("QCF-123-XYZ-20250101.zip")

    def test_init_raises_if_missing_credentials(self) -> None:
        with self.assertRaises(ValueError):
            WesternUnionFTPClientMockNoCredentials()

    def test_disconnect_closes_resources(
        self,
    ) -> None:
        ftp_client = WesternUnionFTPClientMock()
        ftp_client.disconnect()

        ftp_client.client.close.assert_called_once()
        ftp_client._transport.close.assert_called_once()

    def test_get(
        self,
    ) -> None:
        ftp_client = WesternUnionFTPClientMock()
        ftp_client.get("", "")
        ftp_client.client.get.assert_called_once()

        ftp_client.client.get.reset_mock()
        ftp_client.client.get.side_effect = FileNotFoundError("nope")
        ftp_client.get("", "")

    def test_download_returns_bytesio(self) -> None:
        ftp_client = WesternUnionFTPClientMock()

        def fake_getfo(remote: Any, fl: Any) -> None:
            fl.write(b"hello world")

        ftp_client.client.getfo.side_effect = fake_getfo

        fl = ftp_client.download("remote.txt")
        ftp_client.client.getfo.assert_called_once()
        self.assertIsInstance(fl, io.BytesIO)
        self.assertEqual(fl.read(), b"hello world")
