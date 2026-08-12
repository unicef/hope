import pytest

from extras.test_utils.factories import StorageFileFactory

pytestmark = pytest.mark.django_db


def test_str_returns_file_name():
    sf = StorageFileFactory()
    assert str(sf) == "storage.txt"


def test_file_name_property_drops_the_upload_path():
    sf = StorageFileFactory()
    assert sf.file.name.startswith("files/")
    assert sf.file_name == "storage.txt"
