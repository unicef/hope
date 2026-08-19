from collections.abc import Iterator
import logging
from pathlib import Path
from typing import Any
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test.utils import override_settings
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.registration_data.services.rdi_removal import remove_rdi_population
from hope.models import (
    BusinessArea,
    FlexibleAttribute,
    Household,
    Individual,
    Program,
    RegistrationDataImport,
    XlsxUpdateFile,
)

pytestmark = pytest.mark.django_db

ES_REMOVE = "hope.apps.registration_data.services.rdi_removal.remove_elasticsearch_documents_by_matching_ids"


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def active_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def draft_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.DRAFT)


@pytest.fixture
def rdi(business_area: BusinessArea, active_program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area, program=active_program, status=RegistrationDataImport.IN_REVIEW
    )


@pytest.fixture
def household(business_area: BusinessArea, active_program: Program, rdi: RegistrationDataImport) -> Household:
    created = PendingHouseholdFactory(business_area=business_area, program=active_program, registration_data_import=rdi)
    PendingIndividualFactory(
        household=created, business_area=business_area, program=active_program, registration_data_import=rdi
    )
    return created


@pytest.fixture
def unhoused_individual(
    business_area: BusinessArea, active_program: Program, rdi: RegistrationDataImport
) -> Individual:
    return PendingIndividualFactory(
        household=None, business_area=business_area, program=active_program, registration_data_import=rdi
    )


@pytest.fixture
def draft_rdi(business_area: BusinessArea, draft_program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area, program=draft_program, status=RegistrationDataImport.IN_REVIEW
    )


@pytest.fixture
def draft_household(
    business_area: BusinessArea, draft_program: Program, draft_rdi: RegistrationDataImport
) -> Household:
    return PendingHouseholdFactory(
        business_area=business_area, program=draft_program, registration_data_import=draft_rdi
    )


@pytest.fixture
def program_less_rdi(business_area: BusinessArea) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area, program=None, status=RegistrationDataImport.IN_REVIEW
    )


@pytest.fixture
def program_less_household(
    business_area: BusinessArea, active_program: Program, program_less_rdi: RegistrationDataImport
) -> Household:
    return PendingHouseholdFactory(
        business_area=business_area, program=active_program, registration_data_import=program_less_rdi
    )


@pytest.fixture
def rdi_with_files(
    business_area: BusinessArea,
    rdi: RegistrationDataImport,
    household: Household,
    tmp_path: Path,
) -> Iterator[list[str]]:
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        head = household.head_of_household

        head.photo.save("p.png", ContentFile(b"x"), save=True)
        head.disability_certificate_picture.save("c.png", ContentFile(b"x"), save=True)

        document = PendingDocumentFactory(individual=head)
        document.photo.save("d.png", ContentFile(b"x"), save=True)

        household.consent_sign.save("s.png", ContentFile(b"x"), save=True)

        FlexibleAttributeFactory(
            name="img_i_f",
            type=FlexibleAttribute.IMAGE,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        FlexibleAttributeFactory(
            name="img_h_f",
            type=FlexibleAttribute.IMAGE,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        )
        individual_flex_path = default_storage.save("img_i.png", ContentFile(b"x"))
        head.flex_fields["img"] = individual_flex_path
        head.save(update_fields=["flex_fields"])

        household_flex_path = default_storage.save("img_h.png", ContentFile(b"x"))
        household.flex_fields["img_h_f"] = household_flex_path
        household.save(update_fields=["flex_fields"])

        xlsx_update_file = XlsxUpdateFile.objects.create(
            rdi=rdi, business_area=business_area, file=ContentFile(b"x", name="u.xlsx")
        )

        yield [
            head.photo.name,
            head.disability_certificate_picture.name,
            document.photo.name,
            household.consent_sign.name,
            individual_flex_path,
            household_flex_path,
            xlsx_update_file.file.name,
        ]


def test_delete_rdi_true_removes_population_and_sends_captured_ids_to_elasticsearch(
    rdi: RegistrationDataImport,
    household: Household,
    active_program: Program,
    django_assert_num_queries: Any,
) -> None:
    rdi_id = rdi.id
    individual_ids = set(Individual.all_objects.filter(registration_data_import=rdi).values_list("id", flat=True))
    assert len(individual_ids) == 2

    with patch(ES_REMOVE) as mock_remove_es, django_assert_num_queries(63):
        remove_rdi_population(rdi, delete_rdi=True)

    assert not RegistrationDataImport.objects.filter(id=rdi_id).exists()
    assert not Household.all_objects.filter(registration_data_import_id=rdi_id).exists()
    assert not Individual.all_objects.filter(registration_data_import_id=rdi_id).exists()

    assert mock_remove_es.call_count == 2
    ba_slug, code = active_program.business_area.slug, active_program.code
    individuals_call = mock_remove_es.call_args_list[0][0]
    assert set(individuals_call[0]) == individual_ids
    assert individuals_call[1].__name__ == f"IndividualDocument_{ba_slug}_{code}"
    households_call = mock_remove_es.call_args_list[1][0]
    assert set(households_call[0]) == {household.id}
    assert households_call[1].__name__ == f"HouseholdDocument_{ba_slug}_{code}"


def test_delete_rdi_false_keeps_rdi_row_and_removes_population(
    rdi: RegistrationDataImport, household: Household
) -> None:
    with patch(ES_REMOVE):
        remove_rdi_population(rdi, delete_rdi=False)

    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()
    assert not Household.all_objects.filter(registration_data_import=rdi).exists()
    assert not Individual.all_objects.filter(registration_data_import=rdi).exists()


def test_delete_rdi_false_leaves_unhoused_individuals_but_purges_their_es_doc(
    rdi: RegistrationDataImport, household: Household, unhoused_individual: Individual
) -> None:
    with patch(ES_REMOVE) as mock_remove_es:
        remove_rdi_population(rdi, delete_rdi=False)

    assert not Individual.all_objects.filter(id=household.head_of_household_id).exists()
    assert Individual.all_objects.filter(id=unhoused_individual.id).exists()

    purged_individual_ids = set(mock_remove_es.call_args_list[0][0][0])
    assert unhoused_individual.id in purged_individual_ids


def test_skips_elasticsearch_for_non_active_program(
    draft_rdi: RegistrationDataImport, draft_household: Household
) -> None:
    with patch(ES_REMOVE) as mock_remove_es:
        remove_rdi_population(draft_rdi, delete_rdi=False)

    mock_remove_es.assert_not_called()
    assert not Household.all_objects.filter(registration_data_import=draft_rdi).exists()


def test_elasticsearch_failure_propagates_by_default_so_caller_can_roll_back(
    rdi: RegistrationDataImport, household: Household
) -> None:
    with (
        patch(ES_REMOVE, side_effect=Exception("Elasticsearch is down")),
        pytest.raises(Exception, match="Elasticsearch is down"),
    ):
        remove_rdi_population(rdi, delete_rdi=False)


def test_elasticsearch_failure_is_swallowed_and_logged_when_swallow_es_errors_true(
    rdi: RegistrationDataImport, household: Household, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.ERROR, logger="hope.apps.registration_data.services.rdi_removal")

    with patch(ES_REMOVE, side_effect=Exception("Elasticsearch is down")):
        remove_rdi_population(rdi, delete_rdi=False, swallow_es_errors=True)

    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()
    assert not Household.all_objects.filter(registration_data_import=rdi).exists()
    assert not Individual.all_objects.filter(registration_data_import=rdi).exists()
    assert "Failed to remove RDI documents from Elasticsearch" in caplog.text


def test_delete_rdi_true_completes_when_storage_delete_raises(
    rdi: RegistrationDataImport,
    rdi_with_files: list[str],
    django_capture_on_commit_callbacks: Any,
) -> None:
    rdi_id = rdi.id

    with (
        patch(ES_REMOVE),
        patch.object(default_storage, "delete", side_effect=OSError("storage is down")),
        django_capture_on_commit_callbacks(execute=True),
    ):
        remove_rdi_population(rdi, delete_rdi=True)

    assert not RegistrationDataImport.objects.filter(id=rdi_id).exists()
    assert not Household.all_objects.filter(registration_data_import_id=rdi_id).exists()
    assert not Individual.all_objects.filter(registration_data_import_id=rdi_id).exists()
