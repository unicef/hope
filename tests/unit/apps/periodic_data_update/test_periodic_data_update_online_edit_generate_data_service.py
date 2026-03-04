"""Tests for PDU online edit generate data service."""

from typing import Any

from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    FlexibleAttributeForPDUFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PDUOnlineEditFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    SanctionListIndividualFactory,
)
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hope.apps.household.const import FEMALE, MALE
from hope.apps.periodic_data_update.service.periodic_data_update_online_edit_generate_data_service import (
    PDUOnlineEditGenerateDataService,
)
from hope.models import BusinessArea, Individual, Payment, PeriodicFieldData, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=business_area)


@pytest.fixture
def rdi(business_area: BusinessArea) -> Any:
    return RegistrationDataImportFactory(business_area=business_area)


@pytest.fixture
def individuals(business_area: BusinessArea, program: Program, rdi: Any) -> list[Individual]:
    individual1 = IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    individual2 = IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    return [individual1, individual2]


@pytest.fixture
def household(business_area: BusinessArea, program: Program, rdi: Any, individuals: list[Individual]) -> Any:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        head_of_household=individuals[0],
    )
    household.head_of_household = individuals[0]
    household.save()

    for individual in individuals:
        individual.household = household
        individual.save()

    return household


@pytest.fixture
def pdu_field_muac(program: Program) -> Any:
    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL,
        number_of_rounds=5,
        rounds_names=["January", "February", "March", "April", "May"],
    )
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="MUAC",
        pdu_data=pdu_data,
    )


@pytest.fixture
def pdu_field_month_worked(program: Program) -> Any:
    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.BOOL,
        number_of_rounds=5,
        rounds_names=["January", "February", "March", "April", "May"],
    )
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="Month worked",
        pdu_data=pdu_data,
    )


@pytest.fixture
def periodic_data_update_online_edit(business_area: BusinessArea, program: Program) -> Any:
    return PDUOnlineEditFactory(
        program=program,
        business_area=business_area,
    )


@pytest.fixture
def rounds_data() -> list[dict]:
    return [
        {
            "field": "muac",
            "round": 2,
            "round_name": "February",
            "number_of_records": 100,
        },
        {
            "field": "month_worked",
            "round": 4,
            "round_name": "April",
            "number_of_records": 58,
        },
    ]


def test_generate_edit_data(
    program: Program,
    household: Any,
    individuals: list[Individual],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
    rounds_data: list[dict],
) -> None:
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters={},
        rounds_data=rounds_data,
    )
    edit_data = service.generate_edit_data()

    assert edit_data == [
        {
            "individual_uuid": str(individuals[0].pk),
            "unicef_id": individuals[0].unicef_id,
            "first_name": individuals[0].given_name,
            "last_name": individuals[0].family_name,
            "pdu_fields": {
                "muac": {
                    "field_name": "muac",
                    "round_number": 2,
                    "round_name": "February",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "label": "MUAC",
                    "is_editable": True,
                },
                "month_worked": {
                    "field_name": "month_worked",
                    "round_number": 4,
                    "round_name": "April",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.BOOL,
                    "label": "Month worked",
                    "is_editable": True,
                },
            },
        },
        {
            "individual_uuid": str(individuals[1].pk),
            "unicef_id": individuals[1].unicef_id,
            "first_name": individuals[1].given_name,
            "last_name": individuals[1].family_name,
            "pdu_fields": {
                "muac": {
                    "field_name": "muac",
                    "round_number": 2,
                    "round_name": "February",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "label": "MUAC",
                    "is_editable": True,
                },
                "month_worked": {
                    "field_name": "month_worked",
                    "round_number": 4,
                    "round_name": "April",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.BOOL,
                    "label": "Month worked",
                    "is_editable": True,
                },
            },
        },
    ]
    assert len(edit_data) == 2


def test_generate_edit_data_with_one_value_already_set(
    program: Program,
    household: Any,
    individuals: list[Individual],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
    rounds_data: list[dict],
) -> None:
    individual = individuals[0]
    individual.flex_fields = {
        "muac": {
            "2": {
                "value": 20,
                "collection_date": "2021-05-01",
            }
        }
    }
    individual.save()

    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters={},
        rounds_data=rounds_data,
    )
    edit_data = service.generate_edit_data()

    assert edit_data == [
        {
            "individual_uuid": str(individual.pk),
            "unicef_id": individual.unicef_id,
            "first_name": individual.given_name,
            "last_name": individual.family_name,
            "pdu_fields": {
                "muac": {
                    "field_name": "muac",
                    "round_number": 2,
                    "round_name": "February",
                    "value": 20,  # value is already set
                    "collection_date": None,  # collection date is not needed as the value will not be edited
                    "subtype": PeriodicFieldData.DECIMAL,
                    "label": "MUAC",
                    "is_editable": False,
                },
                "month_worked": {
                    "field_name": "month_worked",
                    "round_number": 4,
                    "round_name": "April",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.BOOL,
                    "label": "Month worked",
                    "is_editable": True,
                },
            },
        },
        {
            "individual_uuid": str(individuals[1].pk),
            "unicef_id": individuals[1].unicef_id,
            "first_name": individuals[1].given_name,
            "last_name": individuals[1].family_name,
            "pdu_fields": {
                "muac": {
                    "field_name": "muac",
                    "round_number": 2,
                    "round_name": "February",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "label": "MUAC",
                    "is_editable": True,
                },
                "month_worked": {
                    "field_name": "month_worked",
                    "round_number": 4,
                    "round_name": "April",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.BOOL,
                    "label": "Month worked",
                    "is_editable": True,
                },
            },
        },
    ]
    assert len(edit_data) == 2


def test_generate_edit_data_exclude_individual_with_all_values_set(
    program: Program,
    household: Any,
    individuals: list[Individual],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
    rounds_data: list[dict],
) -> None:
    individual = individuals[0]
    individual.flex_fields = {
        "muac": {
            "2": {
                "value": 20,
                "collection_date": "2021-05-01",
            }
        },
        "month_worked": {
            "4": {
                "value": 20,
                "collection_date": "2021-04-01",
            }
        },
    }
    individual.save()

    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters={},
        rounds_data=rounds_data,
    )
    edit_data = service.generate_edit_data()

    # Only the second individual should be included
    assert edit_data == [
        {
            "individual_uuid": str(individuals[1].pk),
            "unicef_id": individuals[1].unicef_id,
            "first_name": individuals[1].given_name,
            "last_name": individuals[1].family_name,
            "pdu_fields": {
                "muac": {
                    "field_name": "muac",
                    "round_number": 2,
                    "round_name": "February",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "label": "MUAC",
                    "is_editable": True,
                },
                "month_worked": {
                    "field_name": "month_worked",
                    "round_number": 4,
                    "round_name": "April",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.BOOL,
                    "label": "Month worked",
                    "is_editable": True,
                },
            },
        }
    ]
    assert len(edit_data) == 1


def test_get_individuals_queryset_registration_data_import_id_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    rdi1 = RegistrationDataImportFactory(business_area=business_area)
    individual = individuals[0]
    individual.registration_data_import = rdi1
    individual.save()

    filters = {"registration_data_import_id": str(rdi1.pk)}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual


def test_get_individuals_queryset_target_population_id_filter(
    program: Program,
    business_area: BusinessArea,
    rdi: Any,
    household: Any,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    ind1 = IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household2 = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        head_of_household=ind1,
    )
    ind1.household = household2
    ind1.save()

    IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=household2,
    )

    pp = PaymentPlanFactory()
    PaymentFactory(parent=pp, household=household, collector=ind1)

    filters = {"target_population_id": str(pp.pk)}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2
    assert set(queryset) == set(individuals)


def test_get_individuals_queryset_gender_filter(
    program: Program,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    male = individuals[0]
    female = individuals[1]
    male.sex = MALE
    female.sex = FEMALE
    male.save()
    female.save()

    filters = {"gender": FEMALE}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == female


@freeze_time("2024-07-12")
def test_get_individuals_queryset_age_filter(
    program: Program,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual32yo = individuals[0]
    individual29yo = individuals[1]
    individual32yo.birth_date = "1991-10-16"
    individual29yo.birth_date = "1994-10-16"
    individual32yo.save()
    individual29yo.save()

    filters = {"age": {"from": 30, "to": 32}}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual32yo


def test_get_individuals_queryset_registration_date_filter(
    program: Program,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual2023 = individuals[0]
    individual2020 = individuals[1]
    individual2023.first_registration_date = "2023-10-16"
    individual2020.first_registration_date = "2020-10-16"
    individual2023.save()
    individual2020.save()

    filters = {"registration_date": {"from": "2023-10-16", "to": "2023-10-16"}}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual2023


def test_get_individuals_queryset_registration_date_filter_none(
    program: Program,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual2023 = individuals[0]
    individual2020 = individuals[1]
    individual2023.first_registration_date = "2023-10-16"
    individual2020.first_registration_date = "2020-10-16"
    individual2023.save()
    individual2020.save()

    filters = {"registration_date": {"from": None, "to": None}}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2

    filters = {"registration_date": {"from": "2023-10-16"}}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1

    filters = {"registration_date": {"to": "2023-10-16"}}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2


def test_get_individuals_queryset_admin_filter(
    program: Program,
    business_area: BusinessArea,
    rdi: Any,
    household: Any,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    area_type_level_1 = AreaTypeFactory(name="State1", area_level=1)
    area_type_level_2 = AreaTypeFactory(name="State2", area_level=2)
    area1a = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1a")
    area2a = AreaFactory(
        name="City Test2",
        area_type=area_type_level_2,
        p_code="area2a",
        parent=area1a,
    )
    area1b = AreaFactory(name="City Test1b", area_type=area_type_level_1, p_code="area1b")
    area2b = AreaFactory(
        name="City Test2b",
        area_type=area_type_level_2,
        p_code="area2b",
        parent=area1b,
    )

    ind1 = IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household2 = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        admin1=area1b,
        admin2=area2b,
        head_of_household=ind1,
    )
    ind1.household = household2
    ind1.save()

    IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=household2,
    )

    household.admin1 = area1a
    household.save()

    filters = {"admin1": [str(area1a.pk)]}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2
    assert set(queryset) == set(individuals)

    household.admin2 = area2a
    household.save()

    filters = {"admin2": [str(area2a.pk)]}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2
    assert set(queryset) == set(individuals)


def test_get_individuals_queryset_has_grievance_ticket_referral_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
    )
    TicketReferralDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_has_grievance_ticket_referral_exclude_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    individual_without_ticket = individuals[1]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
    )
    TicketReferralDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": False}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_without_ticket


def test_get_individuals_queryset_has_grievance_ticket_negative_feedback_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
    )
    TicketNegativeFeedbackDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_has_grievance_ticket_positive_feedback_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
    )
    TicketPositiveFeedbackDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_has_grievance_ticket_needs_adjudication_filter(
    program: Program,
    business_area: BusinessArea,
    rdi: Any,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    ind1 = IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household2 = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        head_of_household=ind1,
    )
    ind1.household = household2
    ind1.save()

    individual_with_ticket = individuals[0]
    possible_duplicate = individuals[1]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        status=GrievanceTicket.STATUS_NEW,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )
    details = TicketNeedsAdjudicationDetails.objects.create(
        ticket=grievance, golden_records_individual_id=individual_with_ticket.pk
    )
    details.possible_duplicates.add(possible_duplicate)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2
    assert set(queryset) == {individual_with_ticket, possible_duplicate}


def test_get_individuals_queryset_has_grievance_ticket_system_flagging_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
    )
    sanction_list_individual = SanctionListIndividualFactory()
    TicketSystemFlaggingDetails.objects.create(
        ticket=grievance,
        golden_records_individual_id=individual_with_ticket.pk,
        sanction_list_individual=sanction_list_individual,
    )

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_has_grievance_ticket_delete_individual_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        status=GrievanceTicket.STATUS_NEW,
    )
    TicketDeleteIndividualDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_has_grievance_ticket_individual_data_update_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        status=GrievanceTicket.STATUS_NEW,
    )
    TicketIndividualDataUpdateDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_has_grievance_ticket_sensitive_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        status=GrievanceTicket.STATUS_NEW,
        issue_type=GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST,
    )
    TicketSensitiveDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_has_grievance_ticket_complaint_filter(
    program: Program,
    business_area: BusinessArea,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    individual_with_ticket = individuals[0]
    grievance = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
    )
    TicketComplaintDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)

    filters = {"has_grievance_ticket": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 1
    assert queryset.first() == individual_with_ticket


def test_get_individuals_queryset_received_assistance_filter(
    program: Program,
    business_area: BusinessArea,
    rdi: Any,
    household: Any,
    individuals: list[Individual],
    rounds_data: list[dict],
    pdu_field_muac: Any,
    pdu_field_month_worked: Any,
) -> None:
    ind_without_payment1 = IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household_without_payment = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        head_of_household=ind_without_payment1,
    )
    ind_without_payment2 = IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        household=household_without_payment,
    )

    ind_without_payment1.household = household_without_payment
    ind_without_payment1.save()

    individuals_without_payment = [ind_without_payment1, ind_without_payment2]

    PaymentFactory(household=household, collector=individuals[0], status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    filters = {"received_assistance": True}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2
    assert set(queryset) == set(individuals)

    filters = {"received_assistance": False}
    service = PDUOnlineEditGenerateDataService(
        program=program,
        filters=filters,
        rounds_data=rounds_data,
    )
    queryset = service._get_individuals_queryset()
    assert queryset.count() == 2
    assert set(queryset) == set(individuals_without_payment)
