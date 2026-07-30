"""Form-level tests for the CW-only ingest guard on the Aurora RDI admin forms.

`BaseRDIForm.clean` rejects the FLEX ingest when the registration's business area
is `COUNTRY_WORKSPACE_ONLY` (covers both create and amend). `AmendRDIForm.clean`
additionally rejects when the *target* RDI's business area is `COUNTRY_WORKSPACE_ONLY`,
since the form does not constrain the registration and the target RDI to the same BA (BE-09).
"""

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    OrganizationFactory,
    ProgramFactory,
    ProjectFactory,
    RegistrationDataImportFactory,
    RegistrationFactory,
)
from hope.admin.record import AmendRDIForm, BaseRDIForm, CreateRDIForm
from hope.contrib.aurora.models import Registration
from hope.models import BusinessArea, RegistrationDataImport
from hope.models.business_area import ALL_EXCEPT_CW_INGEST_REJECT_MSG

pytestmark = pytest.mark.django_db


def _registration_for_ingest_source(ingest_source: str) -> Registration:
    business_area = BusinessAreaFactory(ingest_source=ingest_source)
    organization = OrganizationFactory(business_area=business_area, slug=business_area.slug)
    project = ProjectFactory(organization=organization)
    return RegistrationFactory(project=project)


def _loading_rdi_for_ingest_source(ingest_source: str) -> RegistrationDataImport:
    business_area = BusinessAreaFactory(ingest_source=ingest_source)
    program = ProgramFactory(business_area=business_area)
    return RegistrationDataImportFactory(
        business_area=business_area, program=program, status=RegistrationDataImport.LOADING
    )


@pytest.fixture
def cw_only_registration() -> Registration:
    return _registration_for_ingest_source(BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY)


@pytest.fixture
def all_except_cw_registration() -> Registration:
    return _registration_for_ingest_source(BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE)


@pytest.fixture
def cw_only_loading_rdi() -> RegistrationDataImport:
    return _loading_rdi_for_ingest_source(BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY)


@pytest.fixture
def all_except_cw_loading_rdi() -> RegistrationDataImport:
    return _loading_rdi_for_ingest_source(BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE)


def test_create_rdi_form_rejects_country_workspace_only_business_area(
    cw_only_registration: Registration,
) -> None:
    form = CreateRDIForm(
        data={
            "registration": cw_only_registration.pk,
            "status": BaseRDIForm.STATUS_TO_IMPORT,
            "filters": "",
            "name": "",
            "is_open": False,
        },
        request=None,
    )

    assert not form.is_valid()
    assert ALL_EXCEPT_CW_INGEST_REJECT_MSG in form.non_field_errors()


def test_create_rdi_form_accepts_all_except_cw_business_area(
    all_except_cw_registration: Registration,
) -> None:
    form = CreateRDIForm(
        data={
            "registration": all_except_cw_registration.pk,
            "status": BaseRDIForm.STATUS_TO_IMPORT,
            "filters": "",
            "name": "",
            "is_open": False,
        },
        request=None,
    )

    assert form.is_valid()


def test_amend_rdi_form_rejects_country_workspace_only_registration(
    cw_only_registration: Registration, all_except_cw_loading_rdi: RegistrationDataImport
) -> None:
    form = AmendRDIForm(
        data={
            "registration": cw_only_registration.pk,
            "rdi": all_except_cw_loading_rdi.pk,
            "status": BaseRDIForm.STATUS_TO_IMPORT,
            "filters": "",
        },
        request=None,
    )

    assert not form.is_valid()
    assert ALL_EXCEPT_CW_INGEST_REJECT_MSG in form.non_field_errors()


def test_amend_rdi_form_rejects_country_workspace_only_target_rdi(
    all_except_cw_registration: Registration, cw_only_loading_rdi: RegistrationDataImport
) -> None:
    form = AmendRDIForm(
        data={
            "registration": all_except_cw_registration.pk,
            "rdi": cw_only_loading_rdi.pk,
            "status": BaseRDIForm.STATUS_TO_IMPORT,
            "filters": "",
        },
        request=None,
    )

    assert not form.is_valid()
    assert ALL_EXCEPT_CW_INGEST_REJECT_MSG in form.non_field_errors()


def test_amend_rdi_form_accepts_all_except_cw(
    all_except_cw_registration: Registration, all_except_cw_loading_rdi: RegistrationDataImport
) -> None:
    form = AmendRDIForm(
        data={
            "registration": all_except_cw_registration.pk,
            "rdi": all_except_cw_loading_rdi.pk,
            "status": BaseRDIForm.STATUS_TO_IMPORT,
            "filters": "",
        },
        request=None,
    )

    assert form.is_valid()
