from typing import Any
from unittest.mock import mock_open, patch

from django.test import TestCase

from hct_mis_api import get_full_version
import pytest


class TestUtils(TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=b'[project]\n version = "2.3.4"')
    def test_get_full_version(self, mock_file_open: Any) -> None:
        assert get_full_version() == "2.3.4"

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_file_open: Any) -> None:
        with pytest.raises(FileNotFoundError):
            get_full_version()

    @patch("builtins.open", new_callable=mock_open, read_data=b'[project]\n wrong_key = "empty_version_XD"')
    def test_key_not_found(self, mock_file_open: Any) -> None:
        with pytest.raises(KeyError):
            get_full_version()
