import pytest

from extras.test_utils.factories import StorageFileFactory

pytestmark = pytest.mark.django_db


def test_str_returns_file_name():
    sf = StorageFileFactory()
    assert str(sf) == sf.file.name


def test_file_name_property():
    sf = StorageFileFactory()
    assert sf.file_name == sf.file.name
