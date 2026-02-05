"""Tests for registration data admin functionality."""

from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from hope.apps.utils.elasticsearch_utils import rebuild_search_index
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
from hope.models.utils import MergeStatusModel
from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketComplaintDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hope.admin.registration_data import RegistrationDataImportAdmin
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
)

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(name="Test program For RDI", business_area=afghanistan)


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

    rebuild_search_index()

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
def test_delete_rdi_merged(django_app: Any, afghanistan: BusinessArea, program: Program) -> None:
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

    rebuild_search_index()

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

    RegistrationDataImportAdmin._delete_merged_rdi(rdi)

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
