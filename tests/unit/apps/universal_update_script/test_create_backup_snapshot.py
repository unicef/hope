import json
from io import BytesIO
from typing import Callable, Tuple

from django.core.files.base import ContentFile

import pytest
from _pytest.monkeypatch import MonkeyPatch
from openpyxl import Workbook

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import MALE, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.universal_update_script.models import UniversalUpdate
from hct_mis_api.apps.universal_update_script.universal_individual_update_service.create_backup_snapshot import (
    create_and_save_snapshot_chunked,
    create_snapshot_content,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def poland() -> Country:
    return Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture
def germany() -> Country:
    return Country.objects.create(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")


@pytest.fixture
def state(poland: Country) -> AreaType:
    return AreaType.objects.create(name="State", country=poland)


@pytest.fixture
def district(poland: Country, state: AreaType) -> AreaType:
    return AreaType.objects.create(name="District", parent=state, country=poland)


@pytest.fixture
def admin1(state: AreaType) -> Area:
    return Area.objects.create(name="Kabul", area_type=state, p_code="AF11")


@pytest.fixture
def admin2(district: AreaType) -> Area:
    return Area.objects.create(name="Kabul1", area_type=district, p_code="AF1115")


@pytest.fixture
def program(poland: Country, germany: Country) -> Program:
    business_area = create_afghanistan()
    business_area.countries.add(poland, germany)

    return ProgramFactory(name="Test Program for Household", status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def individuals(program: Program, admin1: Area, admin2: Area) -> Tuple[Individual, Individual]:
    _, individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0002",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0022",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
            },
        ],
    )
    _, individuals2 = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0003",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0033",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
            },
        ],
    )
    return individuals[0], individuals2[0]


def test_snapshot_json_contains_two_households(program: Program, individuals: Tuple[Individual]) -> None:
    log_message: Callable[[str], None] = lambda message_log: None
    backup_data = json.loads(
        create_snapshot_content(log_message, str(program.id), ["IND-00-0000.0022", "IND-00-0000.0033"])
    )
    assert isinstance(backup_data, list)
    assert len(backup_data) == 2


def test_snapshot_json_generation_with_mocking(monkeypatch: MonkeyPatch, program: Program) -> None:
    uu = UniversalUpdate.objects.create(program=program, unicef_ids="IND-100")

    wb = Workbook()
    ws = wb.active
    ws.append(["unicef_id"])
    ws.append(["IND-100"])
    excel_bytes = BytesIO()
    wb.save(excel_bytes)
    excel_bytes.seek(0)

    uu.update_file.save("update.xlsx", ContentFile(excel_bytes.read()))
    uu.save()

    captured_unicef_ids = []

    def dummy_create_snapshot_content(log_message: Callable[[str], None], program_id: str, unicef_ids: [str]) -> str:
        captured_unicef_ids.extend(unicef_ids)
        return '{"dummy": "snapshot"}'

    monkeypatch.setattr(
        "hct_mis_api.apps.universal_update_script.universal_individual_update_service.create_backup_snapshot.create_snapshot_content",
        dummy_create_snapshot_content,
    )
    create_and_save_snapshot_chunked(uu)
    assert captured_unicef_ids == ["IND-100"]
    backup_content = uu.backup_snapshot.read()
    assert backup_content.decode("utf-8") == '{"dummy": "snapshot"}'


def test_snapshot_json_too_many_unicef_ids(program: Program, individuals: Tuple[Individual]) -> None:
    log_message: Callable[[str], None] = lambda message_log: None
    with pytest.raises(Exception) as exc_info:
        create_snapshot_content(
            log_message, str(program.id), ["IND-00-0000.0022", "IND-00-0000.0033", "IND-00-0000.0044"]
        )
    assert "Some unicef ids are not in the program" in str(exc_info.value)


def test_snapshot_json_generation_no_unicef_id(monkeypatch: MonkeyPatch, program: Program) -> None:
    uu = UniversalUpdate.objects.create(program=program, unicef_ids="IND-100")

    wb = Workbook()
    excel_bytes = BytesIO()
    wb.save(excel_bytes)
    excel_bytes.seek(0)

    uu.update_file.save("update.xlsx", ContentFile(excel_bytes.read()))
    uu.save()

    captured_unicef_ids = []

    def dummy_create_snapshot_content(log_message: Callable[[str], None], program_id: str, unicef_ids: [str]) -> str:
        captured_unicef_ids.extend(unicef_ids)
        return '{"dummy": "snapshot"}'

    monkeypatch.setattr(
        "hct_mis_api.apps.universal_update_script.universal_individual_update_service.create_backup_snapshot.create_snapshot_content",
        dummy_create_snapshot_content,
    )

    with pytest.raises(Exception) as exc_info:
        create_and_save_snapshot_chunked(uu)
    assert "The column 'unicef_id' was not found in the header row." in str(exc_info.value)
