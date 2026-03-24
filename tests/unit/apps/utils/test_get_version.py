from unittest.mock import patch

from hope import get_full_version


@patch("hope.version", return_value="2.3.4")
def test_get_full_version(mock_version) -> None:
    assert get_full_version() == "2.3.4"
