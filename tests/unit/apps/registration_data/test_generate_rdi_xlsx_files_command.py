import pytest

from extras.test_utils.factories import AreaFactory, AreaTypeFactory, CountryFactory
from hope.apps.registration_data.management.commands.generate_rdi_xlsx_files import generate_rdi_xlsx_files

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan_geo() -> dict:
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    admin1_type = AreaTypeFactory(name="Admin 1", country=country, area_level=1)
    admin2_type = AreaTypeFactory(name="Admin 2", country=country, area_level=2, parent=admin1_type)
    admin1 = AreaFactory(name="Admin1", p_code="AF01", area_type=admin1_type)
    admin2 = AreaFactory(name="Admin2", p_code="AF0101", area_type=admin2_type, parent=admin1)
    return {
        "country": country,
        "admin1_type": admin1_type,
        "admin2_type": admin2_type,
        "admin1": admin1,
        "admin2": admin2,
    }


def test_generate_rdi_xlsx_files_command(settings, tmp_path, afghanistan_geo: dict) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)
    settings.PROJECT_ROOT = str(project_root)

    generate_rdi_xlsx_files()

    generated_file = tmp_path / "generated" / "rdi_import_1_hh_1_ind_seed_None.xlsx"
    assert generated_file.exists()
