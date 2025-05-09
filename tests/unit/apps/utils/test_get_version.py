from typing import Any
from unittest.mock import patch

from django.test import TestCase

from hct_mis_api import get_full_version


class TestUtils(TestCase):
    @patch("hct_mis_api.importlib.metadata.version", return_value="2.3.4")
    def test_get_full_version(self, mock_version: Any) -> None:
        self.assertEqual(get_full_version(), "2.3.4")