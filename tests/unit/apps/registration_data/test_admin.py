"""Tests for registration data admin functionality."""

from typing import Any
from unittest.mock import Mock, patch
import uuid

from constance.test import override_config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    ImportDataFactory,
    IndividualFactory,
    KoboImportDataFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketComplaintDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hope.admin.registration_data import (
    RegistrationDataImportAdmin,
    is_country_workspace_rdi_rerun_enabled,
    is_non_country_workspace_rdi_merge_retry_enabled,
)
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
)
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.services.index_management import rebuild_program_indexes
from hope.apps.utils.elasticsearch_utils import ensure_index_ready
from hope.models import (
    BusinessArea,
    Document,
    Household,
    Individual,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.business_area import ALL_EXCEPT_CW_INGEST_REJECT_MSG
from hope.models.utils import MergeStatusModel

pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.xdist_group(name="elasticsearch"),
    pytest.mark.elasticsearch,
]


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(name="Test program For RDI", business_area=afghanistan)


@pytest.fixture
def biometric_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        name="Biometric Program For RDI",
        business_area=afghanistan,
        biometric_deduplication_enabled=True,
    )


@pytest.fixture
def admin_user() -> Any:
    User = get_user_model()  # noqa
    return User.objects.create_superuser(username="root", email="root@root.com", password="password")


@pytest.fixture
def admin_client(admin_user: Any) -> Client:
    client = Client()
    client.login(username="root", password="password")
    return client


@patch("hope.apps.registration_data.celery_tasks.registration_xlsx_import_async_task")
def test_rerun_rdi_xlsx_schedules_async_job(
    mock_registration_xlsx_import_task: Mock,
    admin_client: Client,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    import_data = ImportDataFactory(business_area_slug=afghanistan.slug)
    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.IMPORT_ERROR,
        data_source=RegistrationDataImport.XLS,
        import_data=import_data,
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    mock_registration_xlsx_import_task.assert_called_once_with(
        registration_data_import=rdi,
        import_data_id=str(import_data.id),
        business_area_id=str(afghanistan.id),
        program_id=str(program.id),
    )


@patch("hope.apps.registration_data.celery_tasks.registration_kobo_import_async_task")
def test_rerun_rdi_kobo_schedules_async_job(
    mock_registration_kobo_import_task: Mock,
    admin_client: Client,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    import_data = KoboImportDataFactory(business_area_slug=afghanistan.slug)
    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.IMPORT_ERROR,
        data_source=RegistrationDataImport.KOBO,
        import_data=import_data,
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    mock_registration_kobo_import_task.assert_called_once_with(
        registration_data_import=rdi,
        import_data_id=str(import_data.id),
        business_area_id=str(afghanistan.id),
        program_id=str(program.id),
    )


def test_rerun_rdi_unsupported_data_source_shows_error_message(
    admin_client: Client,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.IMPORT_ERROR,
        data_source=RegistrationDataImport.FLEX_REGISTRATION,
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Cannot rerun RDI if it's not a XLS or KOBO." in messages


@pytest.fixture
def country_workspace_only_business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        name="CW Only",
        slug="cw-only",
        ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY,
    )


@pytest.fixture
def cw_only_program(country_workspace_only_business_area: BusinessArea) -> Program:
    return ProgramFactory(name="CW Only Program", business_area=country_workspace_only_business_area)


@patch("hope.apps.registration_data.celery_tasks.registration_xlsx_import_async_task")
def test_rerun_rdi_rejected_for_country_workspace_only_business_area(
    mock_registration_xlsx_import_task: Mock,
    admin_client: Client,
    country_workspace_only_business_area: BusinessArea,
    cw_only_program: Program,
) -> None:
    import_data = ImportDataFactory(business_area_slug=country_workspace_only_business_area.slug)
    rdi = RegistrationDataImportFactory(
        business_area=country_workspace_only_business_area,
        program=cw_only_program,
        status=RegistrationDataImport.IMPORT_ERROR,
        data_source=RegistrationDataImport.XLS,
        import_data=import_data,
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert ALL_EXCEPT_CW_INGEST_REJECT_MSG in messages
    mock_registration_xlsx_import_task.assert_not_called()


@patch("hope.admin.registration_data.merge_registration_data_import_async_task")
def test_rerun_merge_rdi_schedules_async_job(
    mock_merge_registration_data_import_task: Mock,
    admin_client: Client,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.MERGE_ERROR,
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_merge_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    mock_merge_registration_data_import_task.assert_called_once_with(rdi)


@patch("hope.apps.registration_data.celery_tasks.process_country_workspace_rdi_task")
@patch("hope.admin.registration_data.merge_registration_data_import_async_task")
def test_rerun_cw_rdi_merge_error_routes_to_worker(
    mock_merge: Mock,
    mock_worker: Mock,
    admin_client: Client,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.MERGE_ERROR,
        country_workspace_id=str(uuid.uuid4()),
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_cw_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    mock_worker.assert_called_once_with(rdi)
    mock_merge.assert_not_called()


@patch("hope.apps.registration_data.celery_tasks.process_country_workspace_rdi_task")
@patch("hope.admin.registration_data.merge_registration_data_import_async_task")
def test_rerun_cw_rdi_import_error_routes_to_worker(
    mock_merge: Mock,
    mock_worker: Mock,
    admin_client: Client,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.IMPORT_ERROR,
        country_workspace_id=str(uuid.uuid4()),
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_cw_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    mock_worker.assert_called_once_with(rdi)
    mock_merge.assert_not_called()


@patch("hope.apps.registration_data.celery_tasks.process_country_workspace_rdi_task")
@patch("hope.admin.registration_data.merge_registration_data_import_async_task")
def test_rerun_cw_rdi_merge_scheduled_routes_to_worker(
    mock_merge: Mock,
    mock_worker: Mock,
    admin_client: Client,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.MERGE_SCHEDULED,
        country_workspace_id=str(uuid.uuid4()),
    )

    url = reverse("admin:registration_data_registrationdataimport_rerun_cw_rdi", args=[rdi.pk])
    response = admin_client.post(url)

    assert response.status_code == 302
    mock_worker.assert_called_once_with(rdi)
    mock_merge.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        RegistrationDataImport.IMPORT_ERROR,
        RegistrationDataImport.MERGE_ERROR,
        RegistrationDataImport.MERGE_SCHEDULED,
    ],
)
def test_is_cw_rerunnable_true_for_cw_ingest_invalid_states(status: str) -> None:
    business_area = BusinessArea(ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY)
    rdi = RegistrationDataImport(business_area=business_area, status=status)
    button = type("Button", (), {"original": rdi})()

    assert is_country_workspace_rdi_rerun_enabled(button) is True


@pytest.mark.parametrize(
    ("ingest_source", "status"),
    [
        (BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, RegistrationDataImport.IMPORT_ERROR),
        (BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, RegistrationDataImport.MERGE_ERROR),
        (BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, RegistrationDataImport.MERGE_SCHEDULED),
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, RegistrationDataImport.IN_REVIEW),
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, RegistrationDataImport.MERGED),
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, RegistrationDataImport.MERGING),
    ],
)
def test_is_cw_rerunnable_false_for_non_cw_ingest_or_terminal(ingest_source: str, status: str) -> None:
    business_area = BusinessArea(ingest_source=ingest_source)
    rdi = RegistrationDataImport(business_area=business_area, status=status)
    button = type("Button", (), {"original": rdi})()

    assert is_country_workspace_rdi_rerun_enabled(button) is False


@pytest.mark.parametrize(
    ("ingest_source", "expected"),
    [
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, False),
        (BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, True),
    ],
)
def test_is_non_cw_merge_rerunnable_excludes_cw_ingest(ingest_source: str, expected: bool) -> None:
    business_area = BusinessArea(ingest_source=ingest_source)
    rdi = RegistrationDataImport(business_area=business_area, status=RegistrationDataImport.MERGE_ERROR)
    button = type("Button", (), {"original": rdi})()

    assert is_non_country_workspace_rdi_merge_retry_enabled(button) is expected


@pytest.mark.elasticsearch
def test_delete_rdi_in_review(afghanistan: BusinessArea, program: Program) -> None:
    rdi = RegistrationDataImportFactory(
        name="RDI To Remove",
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.IN_REVIEW,
    )

    pending_individual1 = IndividualFactory(
        household=None,
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        rdi_merge_status=MergeStatusModel.PENDING,
    )

    pending_household = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        rdi_merge_status=MergeStatusModel.PENDING,
        head_of_household=pending_individual1,
    )

    pending_individual1.household = pending_household
    pending_individual1.save()

    IndividualFactory(
        household=pending_household,
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        rdi_merge_status=MergeStatusModel.PENDING,
    )

    DocumentFactory(
        individual=pending_individual1,
        program=program,
        rdi_merge_status=MergeStatusModel.PENDING,
    )

    rebuild_program_indexes(str(program.id))

    assert RegistrationDataImport.objects.count() == 1
    assert PendingHousehold.objects.count() == 1
    assert PendingIndividual.objects.count() == 2
    assert PendingDocument.objects.count() == 1

    RegistrationDataImportAdmin._delete_rdi(rdi)

    assert RegistrationDataImport.objects.count() == 0
    with pytest.raises(RegistrationDataImport.DoesNotExist):
        RegistrationDataImport.objects.get(id=rdi.id)

    assert PendingHousehold.objects.count() == 0
    assert PendingIndividual.objects.count() == 0
    assert PendingDocument.objects.count() == 0


@pytest.mark.elasticsearch
def test_delete_rdi_merged(
    django_app: Any,
    afghanistan: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        name="RDI To Remove",
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.MERGED,
    )

    individual1 = IndividualFactory(
        household=None,
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    household = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        rdi_merge_status=MergeStatusModel.MERGED,
        head_of_household=individual1,
    )

    individual1.household = household
    individual1.save()

    IndividualFactory(
        household=household,
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    document = DocumentFactory(
        individual=individual1,
        program=program,
    )

    grievance_ticket1 = GrievanceTicketFactory(
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
    )
    TicketComplaintDetailsFactory(
        ticket=grievance_ticket1,
        household=household,
    )

    grievance_ticket2 = GrievanceTicketFactory(
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_CLOSED,
    )
    TicketIndividualDataUpdateDetailsFactory(
        ticket=grievance_ticket2,
        individual=individual1,
    )

    User = get_user_model()  # noqa
    admin_user = User.objects.create_superuser(username="root", email="root@root.com", password="password")

    assert GrievanceTicket.objects.count() == 2
    assert TicketIndividualDataUpdateDetails.objects.count() == 1
    assert TicketComplaintDetails.objects.count() == 1
    assert RegistrationDataImport.objects.count() == 1
    assert Household.objects.count() == 1
    assert Individual.objects.count() == 2
    assert Document.objects.count() == 1

    url = reverse("admin:registration_data_registrationdataimport_delete_merged_rdi", args=[rdi.pk])
    response = django_app.get(url, user=admin_user, headers={"X-Root-Token": settings.ROOT_TOKEN})
    assert response.status_code == 200
    content = response.content.decode()
    assert "DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING" in content
    assert "This action will result in removing:" in content

    with override_config(IS_ELASTICSEARCH_ENABLED=True):
        rebuild_program_indexes(str(program.id))

        individual_doc = get_individual_doc(str(program.id))
        household_doc = get_household_doc(str(program.id))
        ensure_index_ready(individual_doc._index._name)
        ensure_index_ready(household_doc._index._name)

        assert individual_doc.search().count() == 2
        assert household_doc.search().count() == 1

        RegistrationDataImportAdmin._delete_merged_rdi(rdi)

        ensure_index_ready(individual_doc._index._name)
        ensure_index_ready(household_doc._index._name)

        assert individual_doc.search().count() == 0
        assert household_doc.search().count() == 0

    assert GrievanceTicket.objects.count() == 0
    assert GrievanceTicket.objects.filter(id=grievance_ticket1.id).first() is None
    assert GrievanceTicket.objects.filter(id=grievance_ticket2.id).first() is None

    assert TicketIndividualDataUpdateDetails.objects.count() == 0
    assert TicketIndividualDataUpdateDetails.objects.filter(ticket=grievance_ticket2).first() is None

    assert TicketComplaintDetails.objects.count() == 0
    assert TicketComplaintDetails.objects.filter(ticket=grievance_ticket1).first() is None

    assert RegistrationDataImport.objects.count() == 0
    assert RegistrationDataImport.objects.filter(id=rdi.id).first() is None

    assert Household.objects.count() == 0
    assert Household.objects.filter(id=household.id).first() is None

    assert Individual.objects.count() == 0
    assert Individual.objects.filter(id=individual1.id).first() is None

    assert Document.objects.count() == 0
    assert Document.objects.filter(id=document.id).first() is None
