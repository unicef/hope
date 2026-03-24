"""Tests for registration data models."""

import datetime
from typing import Any

from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.models import (
    BusinessArea,
    Household,
    Individual,
    IndividualIdentity,
    Partner,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(status=Program.ACTIVE)


@pytest.fixture
def unicef(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef)


@pytest.fixture
def registration_data_import(program: Program, unicef_hq: Partner) -> RegistrationDataImport:
    rdi = RegistrationDataImportFactory(status=RegistrationDataImport.IN_REVIEW, program=program)
    IndividualFactory(
        registration_data_import_id=rdi.id,
        rdi_merge_status=Individual.PENDING,
    )
    IndividualFactory(
        registration_data_import_id=rdi.id,
        rdi_merge_status=Individual.PENDING,
    )
    return rdi


@pytest.fixture
def imported_individual_with_household(
    registration_data_import: RegistrationDataImport,
) -> Individual:
    ind = IndividualFactory(
        full_name="Jane Doe",
        birth_date=datetime.datetime(1991, 3, 4),
        registration_data_import=registration_data_import,
        rdi_merge_status=Individual.PENDING,
    )
    HouseholdFactory(
        registration_data_import=registration_data_import,
        rdi_merge_status=Household.PENDING,
        size=99,
        head_of_household=ind,
    )
    ind.household = ind.household
    ind.save()
    return ind


def test_rdi_can_be_merged(
    registration_data_import: RegistrationDataImport, imported_individual_with_household: Individual
) -> None:
    assert registration_data_import.can_be_merged()


def test_imported_household_str(imported_individual_with_household: Individual) -> None:
    assert str(imported_individual_with_household.household) == imported_individual_with_household.household.unicef_id


@freeze_time("2024-05-27")
def test_imported_individual_age(imported_individual_with_household: Individual) -> None:
    assert imported_individual_with_household.age == 33


def test_imported_individual_str(imported_individual_with_household: Individual) -> None:
    assert str(imported_individual_with_household) == imported_individual_with_household.unicef_id


def test_imported_document_type_str() -> None:
    imported_document_type = DocumentTypeFactory(label="some_label")
    assert str(imported_document_type) == imported_document_type.label


def test_imported_individual_identity_str(
    imported_individual_with_household: Individual,
    unicef_hq: Partner,
) -> None:
    imported_individual_identity = IndividualIdentityFactory(
        individual=imported_individual_with_household,
        number="123456789",
        rdi_merge_status=IndividualIdentity.PENDING,
        partner=unicef_hq,
    )
    assert (
        str(imported_individual_identity)
        == f"UNICEF HQ [Sub-Partner of UNICEF] {imported_individual_with_household.unicef_id} 123456789"
    )


def test_bulk_update_household_size(
    registration_data_import: RegistrationDataImport,
    imported_individual_with_household: Individual,
    program: Program,
) -> None:
    imported_household = imported_individual_with_household.household
    imported_household.refresh_from_db(fields=["size"])
    assert imported_household.size == 99

    registration_data_import.bulk_update_household_size()
    imported_household.refresh_from_db(fields=["size"])
    assert imported_household.size == 99

    # upd DCT recalculate_composition
    program.data_collecting_type.recalculate_composition = True
    program.data_collecting_type.save()

    registration_data_import.bulk_update_household_size()
    imported_household.refresh_from_db(fields=["size"])
    assert imported_household.size == 1
