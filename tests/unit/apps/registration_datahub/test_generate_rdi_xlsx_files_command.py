from django.test import TestCase
import pytest

from extras.test_utils.old_factories.core import create_afghanistan
from extras.test_utils.old_factories.geo import CountryFactory, generate_small_areas_for_afghanistan_only
from hope.apps.registration_datahub.management.commands.generate_rdi_xlsx_files import generate_rdi_xlsx_files


@pytest.mark.django_db
class TestGenerateRdiXlsxFilesCommand(TestCase):
    def test_test_generate_rdi_xlsx_files_command(self) -> None:
        CountryFactory(
            name="Afghanistan",
            short_name="Afghanistan",
            iso_code2="AF",
            iso_code3="AFG",
            iso_num="0004",
        )
        generate_small_areas_for_afghanistan_only()
        create_afghanistan()
        generate_rdi_xlsx_files()
