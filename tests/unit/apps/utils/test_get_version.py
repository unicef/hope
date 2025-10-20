from typing import Any
from unittest.mock import patch

from django.test import TestCase

from hope import get_full_version


class TestUtils(TestCase):
    @patch("hope.version", return_value="2.3.4")
    def test_get_full_version(self, mock_version: Any) -> None:
        assert get_full_version() == "2.3.4"
