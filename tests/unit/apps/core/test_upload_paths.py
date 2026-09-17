from datetime import date
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    FileTempFactory,
    GrievanceDocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    ImportDataFactory,
    IndividualFactory,
    KoboImportDataFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentPlanSupportingDocumentFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    PDUXlsxTemplateFactory,
    PDUXlsxUploadFactory,
    ProgramFactory,
    StorageFileFactory,
    SurveyFactory,
    UniversalUpdateFactory,
    UploadedXLSXFileFactory,
    WesternUnionPaymentPlanReportFactory,
    XLSXKoboTemplateFactory,
    XlsxUpdateFileFactory,
)
from hope.apps.core.upload_paths import build_upload_path, upload_path
from hope.models.payment_plan_supporting_document import PaymentPlanSupportingDocument
from hope.models.program import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(name="Ukraine")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area, code="ab12", start_date=date(2024, 3, 1))


@pytest.fixture
def payment_plan(program: Any) -> Any:
    return PaymentPlanFactory(program_cycle=program.cycles.first())


@pytest.fixture
def individual(business_area: Any, program: Any) -> Any:
    return IndividualFactory(business_area=business_area, program=program)


@pytest.fixture
def document(individual: Any) -> Any:
    return DocumentFactory(individual=individual)


@pytest.fixture
def supporting_document(payment_plan: Any, tmp_path: Any) -> Any:
    # An isolated media root: a file of the same name left by an earlier test run would otherwise
    # make storage append a suffix to the stored name.
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        yield PaymentPlanSupportingDocumentFactory(
            payment_plan=payment_plan,
            file=SimpleUploadedFile("evidence.pdf", b"abc", content_type="application/pdf"),
        )


@pytest.fixture
def file_temp_for_payment_plan(payment_plan: Any) -> Any:
    return FileTempFactory(
        object_id=str(payment_plan.pk),
        content_type=ContentType.objects.get_for_model(payment_plan),
    )


@pytest.fixture
def long_named_supporting_document(payment_plan: Any, tmp_path: Any) -> Any:
    # An isolated media root: a file of the same name left by an earlier test run would otherwise
    # make storage append a suffix to the stored name.
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        yield PaymentPlanSupportingDocumentFactory(
            payment_plan=payment_plan,
            file=SimpleUploadedFile("a" * 300 + ".pdf", b"abc", content_type="application/pdf"),
        )


@pytest.fixture
def file_temp_for_payment_plan_group(program: Any) -> Any:
    group = PaymentPlanGroupFactory(cycle=program.cycles.first())
    return FileTempFactory(
        object_id=str(group.pk),
        content_type=ContentType.objects.get_for_model(group),
    )


@pytest.fixture
def file_temp_for_payment_verification_plan(payment_plan: Any) -> Any:
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
    return FileTempFactory(
        object_id=str(verification_plan.pk),
        content_type=ContentType.objects.get_for_model(verification_plan),
    )


@pytest.fixture
def file_temp_for_western_union_report(payment_plan: Any) -> Any:
    report = WesternUnionPaymentPlanReportFactory(payment_plan=payment_plan)
    return FileTempFactory(
        object_id=str(report.pk),
        content_type=ContentType.objects.get_for_model(report),
    )


@pytest.fixture
def pdu_xlsx_upload(program: Any) -> Any:
    return PDUXlsxUploadFactory(template=PDUXlsxTemplateFactory(program=program))


@pytest.fixture
def file_temp_for_program(program: Any) -> Any:
    return FileTempFactory(
        object_id=str(program.pk),
        content_type=ContentType.objects.get_for_model(program),
    )


@pytest.fixture
def file_temp_for_unregistered_owner(business_area: Any) -> Any:
    return FileTempFactory(
        object_id=str(business_area.pk),
        content_type=ContentType.objects.get_for_model(business_area),
    )


@pytest.fixture
def file_temp_for_missing_owner() -> Any:
    return FileTempFactory(
        object_id="00000000-0000-0000-0000-000000000000",
        content_type=ContentType.objects.get_for_model(Program),
    )


@pytest.fixture
def file_temp_without_owner() -> Any:
    return FileTempFactory()


@pytest.fixture
def storage_file(business_area: Any, tmp_path: Any) -> Any:
    # An isolated media root: a file of the same name left by an earlier test run would otherwise
    # make storage append a suffix to the stored name.
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        with freeze_time("2026-09-09 12:00:00"):
            file = StorageFileFactory(
                business_area=business_area,
                file=SimpleUploadedFile("holdings.xlsx", b"abc"),
            )
        yield file


@pytest.fixture
def import_data() -> Any:
    return ImportDataFactory(business_area_slug="ukraine")


@pytest.fixture
def kobo_import_data() -> Any:
    return KoboImportDataFactory(business_area_slug="ukraine")


@pytest.fixture
def survey(business_area: Any, program: Any) -> Any:
    return SurveyFactory(business_area=business_area, program=program)


@pytest.fixture
def household(business_area: Any, program: Any) -> Any:
    return HouseholdFactory(business_area=business_area, program=program)


@pytest.fixture
def universal_update(program: Any) -> Any:
    return UniversalUpdateFactory(program=program)


@pytest.fixture
def xlsx_update_file_without_program(business_area: Any) -> Any:
    return XlsxUpdateFileFactory(business_area=business_area, program=None)


@pytest.fixture
def kobo_template() -> Any:
    return XLSXKoboTemplateFactory()


@pytest.fixture
def uploaded_sanction_list_file() -> Any:
    return UploadedXLSXFileFactory()


@pytest.fixture
def grievance_document_in_program(business_area: Any, program: Any) -> Any:
    ticket = GrievanceTicketFactory(business_area=business_area)
    ticket.programs.add(program)
    return GrievanceDocumentFactory(grievance_ticket=ticket)


@pytest.fixture
def grievance_document_without_program(business_area: Any) -> Any:
    return GrievanceDocumentFactory(grievance_ticket=GrievanceTicketFactory(business_area=business_area))


@pytest.fixture
def grievance_ticket_in_program(business_area: Any, program: Any) -> Any:
    ticket = GrievanceTicketFactory(business_area=business_area)
    ticket.programs.add(program)
    return ticket


@pytest.mark.parametrize(
    ("business_area_slug", "program_code", "expected"),
    [
        pytest.param("ukraine", "ab12", "2024/ukraine/ab12/report.xlsx", id="business-area-and-programme"),
        pytest.param("ukraine", None, "2024/ukraine/_unassigned/report.xlsx", id="no-programme"),
        pytest.param("ukraine", "", "2024/ukraine/_unassigned/report.xlsx", id="blank-programme"),
        pytest.param(None, None, "2024/_global/report.xlsx", id="no-business-area"),
        pytest.param(None, "ab12", "2024/_global/report.xlsx", id="programme-without-business-area"),
    ],
)
def test_build_upload_path_nests_the_scope_it_is_given(
    business_area_slug: str | None, program_code: str | None, expected: str
) -> None:
    path = build_upload_path("report.xlsx", year=2024, business_area_slug=business_area_slug, program_code=program_code)

    assert path == expected


@pytest.mark.parametrize(
    ("business_area_slug", "program_code", "expected"),
    [
        pytest.param("ukraine", "a/b", "2024/ukraine/a_b/report.xlsx", id="separator-in-the-programme"),
        pytest.param("ukraine", "..", "2024/ukraine/_unassigned/report.xlsx", id="parent-directory-as-the-programme"),
        pytest.param("ukraine", "a.b", "2024/ukraine/a_b/report.xlsx", id="dot-in-the-programme"),
        pytest.param("ukraine", "///", "2024/ukraine/_unassigned/report.xlsx", id="only-separators-as-the-programme"),
        pytest.param("../etc", "ab12", "2024/___etc/ab12/report.xlsx", id="parent-directory-in-the-business-area"),
    ],
)
def test_build_upload_path_sanitises_the_scope_segments(
    business_area_slug: str, program_code: str, expected: str
) -> None:
    path = build_upload_path("report.xlsx", year=2024, business_area_slug=business_area_slug, program_code=program_code)

    assert path == expected


def test_build_upload_path_keeps_only_the_filename() -> None:
    path = build_upload_path("../../etc/passwd", year=2024, business_area_slug="ukraine", program_code="ab12")

    assert path == "2024/ukraine/ab12/passwd"


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        pytest.param("a" * 300 + ".xlsx", "2024/ukraine/ab12/" + "a" * 224 + ".xlsx", id="with-an-extension"),
        pytest.param("a" * 300, "2024/ukraine/ab12/" + "a" * 229, id="without-an-extension"),
    ],
)
def test_build_upload_path_truncates_a_long_filename(filename: str, expected: str) -> None:
    path = build_upload_path(filename, year=2024, business_area_slug="ukraine", program_code="ab12")

    assert path == expected


@freeze_time("2026-09-09 12:00:00")
def test_build_upload_path_uses_the_upload_year_when_no_year_is_given() -> None:
    path = build_upload_path("report.xlsx", business_area_slug="ukraine", program_code="ab12")

    assert path == "2026/ukraine/ab12/report.xlsx"


@freeze_time("2026-09-09 12:00:00")
@pytest.mark.parametrize(
    ("instance_fixture", "filename", "expected"),
    [
        pytest.param("individual", "photo.jpg", "2024/ukraine/ab12/photo.jpg", id="programme-on-the-instance"),
        pytest.param("document", "photo.jpg", "2024/ukraine/ab12/photo.jpg", id="programme-through-a-relation"),
        pytest.param(
            "supporting_document", "report.pdf", "2024/ukraine/ab12/report.pdf", id="programme-through-a-chain"
        ),
        pytest.param(
            "grievance_document_in_program", "report.pdf", "2024/ukraine/ab12/report.pdf", id="first-of-a-many-to-many"
        ),
        pytest.param(
            "grievance_ticket_in_program", "photo.jpg", "2024/ukraine/ab12/photo.jpg", id="programme-of-a-ticket"
        ),
        pytest.param(
            "file_temp_for_payment_plan", "report.xlsx", "2024/ukraine/ab12/report.xlsx", id="owner-payment-plan"
        ),
        pytest.param(
            "file_temp_for_payment_plan_group",
            "report.xlsx",
            "2024/ukraine/ab12/report.xlsx",
            id="owner-payment-plan-group",
        ),
        pytest.param(
            "file_temp_for_payment_verification_plan",
            "report.xlsx",
            "2024/ukraine/ab12/report.xlsx",
            id="owner-payment-verification-plan",
        ),
        pytest.param(
            "file_temp_for_western_union_report",
            "report.xlsx",
            "2024/ukraine/ab12/report.xlsx",
            id="owner-western-union-report",
        ),
        pytest.param(
            "pdu_xlsx_upload", "report.xlsx", "2024/ukraine/ab12/report.xlsx", id="periodic-data-update-template"
        ),
        pytest.param(
            "file_temp_for_program", "report.xlsx", "2024/ukraine/ab12/report.xlsx", id="owner-is-the-programme"
        ),
        pytest.param(
            "grievance_document_without_program",
            "report.pdf",
            "2026/ukraine/_unassigned/report.pdf",
            id="business-area-of-the-ticket",
        ),
        pytest.param(
            "storage_file", "report.xlsx", "2026/ukraine/_unassigned/report.xlsx", id="business-area-without-programme"
        ),
        pytest.param(
            "kobo_import_data",
            "submissions.json",
            "2026/ukraine/_unassigned/submissions.json",
            id="business-area-slug-inherited-from-a-parent-table",
        ),
        pytest.param(
            "xlsx_update_file_without_program",
            "update.xlsx",
            "2026/ukraine/_unassigned/update.xlsx",
            id="nullable-programme-left-empty",
        ),
        pytest.param("survey", "sample.xlsx", "2024/ukraine/ab12/sample.xlsx", id="survey-programme"),
        pytest.param("household", "consent.png", "2024/ukraine/ab12/consent.png", id="household-programme"),
        pytest.param(
            "universal_update", "template.xlsx", "2024/ukraine/ab12/template.xlsx", id="universal-update-programme"
        ),
        pytest.param("kobo_template", "template.xlsx", "2026/_global/template.xlsx", id="kobo-template-is-global"),
        pytest.param(
            "import_data", "report.xlsx", "2026/ukraine/_unassigned/report.xlsx", id="business-area-slug-held-as-text"
        ),
        pytest.param(
            "file_temp_for_unregistered_owner", "report.xlsx", "2026/_global/report.xlsx", id="owner-has-no-programme"
        ),
        pytest.param(
            "file_temp_for_missing_owner", "report.xlsx", "2026/_global/report.xlsx", id="owner-no-longer-exists"
        ),
        pytest.param("file_temp_without_owner", "report.xlsx", "2026/_global/report.xlsx", id="no-owner"),
        pytest.param("uploaded_sanction_list_file", "report.xlsx", "2026/_global/report.xlsx", id="no-scope-at-all"),
    ],
)
def test_upload_path_resolves_the_scope_of_the_instance(
    request: pytest.FixtureRequest, instance_fixture: str, filename: str, expected: str
) -> None:
    path = upload_path(request.getfixturevalue(instance_fixture), filename)

    assert path == expected


def test_a_saved_file_is_stored_under_its_programme(supporting_document: Any) -> None:
    assert supporting_document.file.name == "2024/ukraine/ab12/evidence.pdf"


@freeze_time("2026-09-09 12:00:00")
def test_a_saved_file_without_a_programme_is_stored_under_its_business_area(storage_file: Any) -> None:
    assert storage_file.file.name == "2026/ukraine/_unassigned/holdings.xlsx"


def test_a_long_file_name_survives_a_round_trip_through_the_column(long_named_supporting_document: Any) -> None:
    stored = PaymentPlanSupportingDocument.objects.get(pk=long_named_supporting_document.pk)

    assert stored.file.name == "2024/ukraine/ab12/" + "a" * 225 + ".pdf"
    assert len(stored.file.name) == 247
