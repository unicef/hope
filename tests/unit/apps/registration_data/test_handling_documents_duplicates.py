import datetime

from django.db import DEFAULT_DB_ALIAS, connections
from django.test.utils import CaptureQueriesContext
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.household.const import FEMALE, HEAD, MALE, SON_DAUGHTER, WIFE_HUSBAND
from hope.apps.registration_data.tasks.deduplicate import HardDocumentDeduplication
from hope.models import Document
from hope.models.utils import MergeStatusModel

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]


@pytest.fixture
def poland_country() -> object:
    return CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616")


@pytest.fixture
def business_area() -> object:
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        has_data_sharing_agreement=True,
    )


@pytest.fixture
def program(business_area: object) -> object:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def registration_data_import(business_area: object, program: object) -> object:
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def document_types() -> dict:
    national_id = DocumentTypeFactory(label="national_id", key="national_id", valid_for_deduplication=False)
    tax_id = DocumentTypeFactory(label="tax_id", key="tax_id", valid_for_deduplication=False)
    return {"national_id": national_id, "tax_id": tax_id}


@pytest.fixture
def head_individual(business_area: object, program: object, registration_data_import: object) -> object:
    return IndividualFactory(
        household=None,
        registration_data_import=registration_data_import,
        business_area=business_area,
        program=program,
        given_name="Test",
        full_name="Test Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
        relationship=HEAD,
        sex=MALE,
        birth_date=datetime.date(1955, 9, 7),
    )


@pytest.fixture
def household(
    head_individual: object, business_area: object, program: object, registration_data_import: object
) -> object:
    return HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        head_of_household=head_individual,
        create_role=False,
        rdi_merge_status=MergeStatusModel.MERGED,
    )


@pytest.fixture
def individuals(
    household: object,
    head_individual: object,
    business_area: object,
    program: object,
    registration_data_import: object,
) -> list:
    individuals = [
        head_individual,
        IndividualFactory(
            household=household,
            registration_data_import=registration_data_import,
            business_area=business_area,
            program=program,
            given_name="Tesa",
            full_name="Tesa Testowski",
            middle_name="",
            family_name="Testowski",
            phone_no="453-85-423",
            phone_no_alternative="",
            relationship=WIFE_HUSBAND,
            sex=FEMALE,
            birth_date=datetime.date(1955, 9, 5),
        ),
        IndividualFactory(
            household=household,
            registration_data_import=registration_data_import,
            business_area=business_area,
            program=program,
            given_name="Example",
            full_name="Example Example",
            middle_name="",
            family_name="Example",
            phone_no="934-25-25-121",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=MALE,
            birth_date=datetime.date(1985, 8, 12),
        ),
        IndividualFactory(
            household=household,
            registration_data_import=registration_data_import,
            business_area=business_area,
            program=program,
            given_name="Example",
            full_name="Example Example",
            middle_name="",
            family_name="Example",
            phone_no="934-25-25-121",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=MALE,
            birth_date=datetime.date(1985, 8, 12),
        ),
        IndividualFactory(
            household=household,
            registration_data_import=registration_data_import,
            business_area=business_area,
            program=program,
            given_name="Example",
            full_name="Example Example",
            middle_name="",
            family_name="Example",
            phone_no="934-25-25-121",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=MALE,
            birth_date=datetime.date(1985, 8, 12),
        ),
        IndividualFactory(
            household=household,
            registration_data_import=registration_data_import,
            business_area=business_area,
            program=program,
            given_name="Example",
            full_name="Example Example",
            middle_name="",
            family_name="Example",
            phone_no="123-45-67-899",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=MALE,
            birth_date=datetime.date(1985, 8, 12),
        ),
    ]
    household.head_of_household = head_individual
    household.save(update_fields=["head_of_household"])
    return individuals


@pytest.fixture
def documents(
    individuals: list,
    poland_country: object,
    document_types: dict,
) -> dict:
    document1 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="ASD123",
        individual=individuals[0],
        status=Document.STATUS_VALID,
    )
    document2 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="ASD123",
        individual=individuals[1],
    )
    document3 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="BBC999",
        individual=individuals[2],
    )
    document4 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="ASD123",
        individual=individuals[3],
    )
    document5 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="TOTALY UNIQ",
        individual=individuals[4],
        status=Document.STATUS_VALID,
    )
    document6 = DocumentFactory(
        country=poland_country,
        type=document_types["tax_id"],
        document_number="ASD123",
        individual=individuals[2],
        status=Document.STATUS_VALID,
    )
    document7 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="ASD123",
        individual=individuals[1],
    )
    document8 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="ASD123",
        individual=individuals[4],
    )
    document9 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="UNIQ",
        individual=individuals[5],
    )
    return {
        "document1": document1,
        "document2": document2,
        "document3": document3,
        "document4": document4,
        "document5": document5,
        "document6": document6,
        "document7": document7,
        "document8": document8,
        "document9": document9,
        "all": [
            document1,
            document2,
            document3,
            document4,
            document5,
            document6,
            document7,
            document8,
            document9,
        ],
    }


def test_hard_documents_deduplication(documents: dict, registration_data_import: object, household: object) -> None:
    docs = [documents["document2"], documents["document3"], documents["document4"]]
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[doc.id for doc in docs]),
        registration_data_import,
    )
    for doc in documents["all"]:
        doc.refresh_from_db()
    assert documents["document1"].status == Document.STATUS_VALID
    assert documents["document2"].status == Document.STATUS_NEED_INVESTIGATION
    assert documents["document3"].status == Document.STATUS_VALID
    assert documents["document4"].status == Document.STATUS_NEED_INVESTIGATION
    assert GrievanceTicket.objects.count() == 1
    grievance_ticket = GrievanceTicket.objects.first()
    assert grievance_ticket.programs.count() == 1
    assert grievance_ticket.programs.first().id == household.program.id
    ticket_details = grievance_ticket.needs_adjudication_ticket_details
    assert ticket_details.possible_duplicates.count() == 2
    assert ticket_details.is_multiple_duplicates_version is True

    household.refresh_from_db()
    assert grievance_ticket.household_unicef_id == household.unicef_id


def test_hard_documents_deduplication_for_initially_valid(documents: dict, registration_data_import: object) -> None:
    doc = documents["document5"]
    HardDocumentDeduplication().deduplicate(Document.objects.filter(id__in=[doc.id]), registration_data_import)
    doc.refresh_from_db()
    assert doc.status == Document.STATUS_VALID
    assert GrievanceTicket.objects.count() == 0


def test_should_create_one_ticket(documents: dict, registration_data_import: object) -> None:
    docs = [documents["document2"], documents["document3"], documents["document4"]]
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[doc.id for doc in docs]),
        registration_data_import,
    )
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[doc.id for doc in docs]),
        registration_data_import,
    )
    assert GrievanceTicket.objects.count() == 1


def test_hard_documents_deduplication_number_of_queries(documents: dict, registration_data_import: object) -> None:
    docs1 = [
        documents["document2"],
        documents["document3"],
        documents["document4"],
        documents["document5"],
    ]
    docs2 = [
        documents["document2"],
        documents["document3"],
        documents["document4"],
        documents["document5"],
        documents["document7"],
        documents["document8"],
    ]
    context = CaptureQueriesContext(connection=connections[DEFAULT_DB_ALIAS])
    with context:
        HardDocumentDeduplication().deduplicate(
            Document.objects.filter(id__in=[doc.id for doc in docs1]),
            registration_data_import,
        )
        first_dedup_query_count = len(context.captured_queries)
        HardDocumentDeduplication().deduplicate(
            Document.objects.filter(id__in=[doc.id for doc in docs2]),
            registration_data_import,
        )
        second_dedup_query_count = len(context.captured_queries) - first_dedup_query_count
        assert first_dedup_query_count == second_dedup_query_count, "Both queries should use same amount of queries"
        assert first_dedup_query_count == 13, "Should only use 14 queries"


def test_ticket_created_correctly(documents: dict, registration_data_import: object, program: object) -> None:
    docs = [
        documents["document2"],
        documents["document3"],
        documents["document4"],
        documents["document5"],
    ]
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[doc.id for doc in docs]),
        registration_data_import,
    )
    for doc in documents["all"]:
        doc.refresh_from_db()

    assert GrievanceTicket.objects.count() == 1

    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[documents["document7"].id]),
        registration_data_import,
    )
    assert GrievanceTicket.objects.count() == 1
    grievance_ticket = GrievanceTicket.objects.first()
    assert grievance_ticket.programs.count() == 1
    assert grievance_ticket.programs.first().id == program.id


def test_valid_for_deduplication_doc_type(
    poland_country: object,
    document_types: dict,
    individuals: list,
    registration_data_import: object,
) -> None:
    dt_tax_id = document_types["tax_id"]
    dt_national_id = document_types["national_id"]
    DocumentFactory(
        country=poland_country,
        type=dt_tax_id,
        document_number="TAX_ID_DOC_123",
        individual=individuals[2],
        status=Document.STATUS_VALID,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    doc_national_id_1 = DocumentFactory(
        country=poland_country,
        type=dt_national_id,
        document_number="TAX_ID_DOC_123",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    doc_national_id_2 = DocumentFactory(
        country=poland_country,
        type=dt_national_id,
        document_number="TAX_ID_DOC_123",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[doc_national_id_1.id]), registration_data_import
    )
    doc_national_id_1.refresh_from_db()
    assert doc_national_id_1.status == Document.STATUS_NEED_INVESTIGATION

    dt_national_id.valid_for_deduplication = True
    dt_national_id.save()

    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[doc_national_id_2.id]), registration_data_import
    )
    doc_national_id_2.refresh_from_db()
    assert doc_national_id_2.status == Document.STATUS_VALID


def test_hard_documents_deduplication_for_invalid_document(
    documents: dict, registration_data_import: object, individuals: list
) -> None:
    individuals[5].withdraw()
    documents["document9"].refresh_from_db()
    assert documents["document9"].status == Document.STATUS_INVALID
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[documents["document9"].id]),
        registration_data_import,
    )
    documents["document9"].refresh_from_db()
    assert documents["document9"].status == Document.STATUS_INVALID


def test_hard_documents_deduplication_for_the_diff_program(
    business_area: object,
    registration_data_import: object,
    poland_country: object,
    document_types: dict,
) -> None:
    program_2 = ProgramFactory(business_area=business_area)
    registration_data_import_2 = RegistrationDataImportFactory(business_area=business_area, program=program_2)
    household = HouseholdFactory(
        business_area=business_area,
        program=program_2,
        registration_data_import=registration_data_import_2,
    )
    individual = IndividualFactory(
        household=household,
        business_area=business_area,
        program=program_2,
        registration_data_import=registration_data_import_2,
        relationship=HEAD,
    )
    new_document_from_other_program = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="ASD123",
        individual=individual,
        status=Document.STATUS_PENDING,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    individual.refresh_from_db()
    assert str(individual.program_id) == str(program_2.pk)
    new_document_from_other_program.refresh_from_db()
    assert new_document_from_other_program.status == Document.STATUS_PENDING

    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[new_document_from_other_program.id]),
        registration_data_import_2,
    )
    new_document_from_other_program.refresh_from_db()
    assert new_document_from_other_program.status == Document.STATUS_VALID


def test_ticket_creation_for_the_same_ind_doc_numbers(
    poland_country: object,
    document_types: dict,
    individuals: list,
    registration_data_import: object,
) -> None:
    passport = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    tax_id = DocumentFactory(
        country=poland_country,
        type=document_types["tax_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d1 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="222",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="222",
        individual=individuals[1],
        status=Document.STATUS_VALID,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d2 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="333",
        individual=individuals[3],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d3 = DocumentFactory(
        country=poland_country,
        type=document_types["tax_id"],
        document_number="333",
        individual=individuals[4],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d4 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="444",
        individual=individuals[0],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d5 = DocumentFactory(
        country=poland_country,
        type=document_types["tax_id"],
        document_number="444",
        individual=individuals[1],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d6 = DocumentFactory(
        country=poland_country,
        type=DocumentTypeFactory(label="other_type", key="other_type"),
        document_number="444",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    assert GrievanceTicket.objects.count() == 0
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[passport.id, tax_id.id, d1.id, d2.id, d3.id, d4.id, d5.id, d6.id]),
        registration_data_import,
    )

    assert GrievanceTicket.objects.count() == 3

    passport.refresh_from_db()
    assert passport.status == Document.STATUS_VALID

    tax_id.refresh_from_db()
    assert tax_id.status == Document.STATUS_VALID


def test_ticket_creation_for_the_same_ind_and_across_other_inds_doc_numbers(
    poland_country: object,
    document_types: dict,
    individuals: list,
    registration_data_import: object,
) -> None:
    passport = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    tax_id = DocumentFactory(
        country=poland_country,
        type=document_types["tax_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d1 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="222",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d2 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="111",
        individual=individuals[3],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    assert GrievanceTicket.objects.count() == 0
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[passport.id, tax_id.id, d1.id, d2.id]),
        registration_data_import,
    )

    assert GrievanceTicket.objects.count() == 1
    ticket_details = TicketNeedsAdjudicationDetails.objects.first()
    assert ticket_details.golden_records_individual is not None
    assert ticket_details.possible_duplicates.count() == 1
    assert ticket_details.golden_records_individual != ticket_details.possible_duplicates.first()

    passport.refresh_from_db()
    assert passport.status == Document.STATUS_VALID
    tax_id.refresh_from_db()
    assert tax_id.status == Document.STATUS_VALID
    d2.refresh_from_db()
    assert d2.status == Document.STATUS_NEED_INVESTIGATION


def test_ticket_creation_for_the_same_ind_doc_numbers_same_doc_type(
    poland_country: object,
    document_types: dict,
    individuals: list,
    registration_data_import: object,
) -> None:
    Document.objects.all().delete()
    passport = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    passport2 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d1 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="222",
        individual=individuals[1],
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    assert GrievanceTicket.objects.count() == 0
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[passport.id, passport2.id, d1.id]),
        registration_data_import,
    )

    assert GrievanceTicket.objects.count() == 0

    passport.refresh_from_db()
    assert passport.status == Document.STATUS_INVALID

    passport2.refresh_from_db()
    assert passport2.status == Document.STATUS_VALID
    assert GrievanceTicket.objects.count() == 0


def test_ticket_creation_for_the_same_ind_doc_numbers_different_doc_type(
    poland_country: object,
    document_types: dict,
    individuals: list,
    registration_data_import: object,
) -> None:
    Document.objects.all().delete()
    passport = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    passport2 = DocumentFactory(
        country=poland_country,
        type=document_types["tax_id"],
        document_number="111",
        individual=individuals[2],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    d1 = DocumentFactory(
        country=poland_country,
        type=document_types["national_id"],
        document_number="222",
        individual=individuals[1],
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    assert GrievanceTicket.objects.count() == 0
    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(id__in=[passport.id, passport2.id, d1.id]),
        registration_data_import,
    )

    assert GrievanceTicket.objects.count() == 0

    passport.refresh_from_db()
    assert passport.status == Document.STATUS_VALID

    passport2.refresh_from_db()
    assert passport2.status == Document.STATUS_VALID
    assert GrievanceTicket.objects.count() == 0
