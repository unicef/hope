from pathlib import Path
from typing import Any

from django.core.files.base import ContentFile
import pytest

from extras.test_utils.factories import UniversalUpdateFactory
from hope.models import UniversalUpdate

pytestmark = pytest.mark.django_db()


@pytest.fixture
def media_root(settings: Any, tmp_path: Path) -> Path:
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


@pytest.fixture
def universal_update() -> UniversalUpdate:
    return UniversalUpdateFactory()


@pytest.fixture
def other_universal_update() -> UniversalUpdate:
    return UniversalUpdateFactory()


def test_two_jobs_saving_the_same_template_name_keep_separate_files(
    media_root: Path, universal_update: UniversalUpdate, other_universal_update: UniversalUpdate
) -> None:
    universal_update.template_file.save("template.xlsx", ContentFile(b"first"))
    other_universal_update.template_file.save("template.xlsx", ContentFile(b"second"))

    assert universal_update.template_file.name != other_universal_update.template_file.name
    assert universal_update.template_file.read() == b"first"
    assert other_universal_update.template_file.read() == b"second"


def test_two_jobs_saving_the_same_snapshot_name_keep_separate_files(
    media_root: Path, universal_update: UniversalUpdate, other_universal_update: UniversalUpdate
) -> None:
    universal_update.backup_snapshot.save("snapshot.json", ContentFile(b"first"))
    other_universal_update.backup_snapshot.save("snapshot.json", ContentFile(b"second"))

    assert universal_update.backup_snapshot.name != other_universal_update.backup_snapshot.name
    assert universal_update.backup_snapshot.read() == b"first"
    assert other_universal_update.backup_snapshot.read() == b"second"
