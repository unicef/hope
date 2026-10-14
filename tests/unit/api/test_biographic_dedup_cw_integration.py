import itertools
from typing import Any
from unittest.mock import patch
import uuid

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    IndividualFactory,
    RegistrationDataImportFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.household.const import DUPLICATE, DUPLICATE_IN_BATCH, HEAD, UNIQUE, UNIQUE_IN_BATCH
from hope.models import (
    BusinessArea,
    Country,
    DataCollectingType,
    Individual,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
]


@pytest.fixture
def warm_content_type_cache() -> None:
    ContentType.objects.get_for_models(*apps.get_models())


@pytest.fixture
def mock_deduplication_engine_env_vars(settings) -> None:
    settings.DEDUPLICATION_ENGINE_API_KEY = "TEST"
    settings.DEDUPLICATION_ENGINE_API_URL = "TEST/"


@pytest.fixture
def eager_celery() -> Any:
    from hope.apps.core.celery import app as celery_app

    prev_always_eager = celery_app.conf.task_always_eager
    prev_eager_propagates = celery_app.conf.task_eager_propagates
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True

    yield

    celery_app.conf.task_always_eager = prev_always_eager
    celery_app.conf.task_eager_propagates = prev_eager_propagates


@pytest.fixture
def user_business_area(user_business_area: BusinessArea) -> BusinessArea:
    user_business_area.ingest_source = BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY
    user_business_area.save(update_fields=["ingest_source"])
    return user_business_area


@pytest.fixture
def social_program(user_business_area: BusinessArea) -> Program:
    dct = DataCollectingTypeFactory(
        label="Full",
        code="full",
        type=DataCollectingType.Type.SOCIAL.value,
    )
    dct.limit_to.add(user_business_area)
    beneficiary_group = BeneficiaryGroupFactory(master_detail=False)
    return ProgramFactory(
        status=Program.ACTIVE,
        business_area=user_business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
        biometric_deduplication_enabled=False,
    )


@pytest.fixture
def population_rdi(social_program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=social_program,
        business_area=social_program.business_area,
        status=RegistrationDataImport.MERGED,
    )


@pytest.fixture
def population(social_program: Program, population_rdi: RegistrationDataImport) -> dict[str, Individual]:
    people = [
        ("cw-pop-single", "Jonas", "Becker", "MALE", "1987-03-14", "", ""),
        ("cw-pop-multi-name", "Lucia", "Fernandez", "FEMALE", "1966-02-02", "", ""),
        ("cw-pop-multi-phone", "Halina", "Wrobel", "FEMALE", "1993-08-21", "+48600111222", "+48600111333"),
        ("cw-pop-mixed", "Pavel", "Novak", "MALE", "1955-06-06", "", ""),
        ("cw-pop-swallowed-a", "Fatima", "Rahimi", "FEMALE", "1992-07-04", "", ""),
        ("cw-pop-swallowed-b", "Fatima", "Rahimi", "FEMALE", "1992-07-04", "", ""),
    ]
    return {
        cw_id: IndividualFactory(
            program=social_program,
            business_area=social_program.business_area,
            registration_data_import=population_rdi,
            country_workspace_id=cw_id,
            given_name=given_name,
            family_name=family_name,
            full_name=f"{given_name} {family_name}",
            sex=sex,
            birth_date=birth_date,
            phone_no=phone_no,
            phone_no_alternative=phone_no_alternative,
            relationship=HEAD,
        )
        for cw_id, given_name, family_name, sex, birth_date, phone_no, phone_no_alternative in people
    }


@pytest.fixture
def population_open_biographic_ticket(
    population: dict[str, Individual], population_rdi: RegistrationDataImport
) -> TicketNeedsAdjudicationDetails:
    details = TicketNeedsAdjudicationDetailsFactory(
        ticket__business_area=population_rdi.business_area,
        ticket__registration_data_import=population_rdi,
        ticket__issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        golden_records_individual=population["cw-pop-swallowed-a"],
        is_multiple_duplicates_version=True,
    )
    details.possible_duplicates.add(population["cw-pop-swallowed-b"])
    return details


@pytest.fixture
def deterministic_individual_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    # Field caches uuid.uuid4 in _get_default, so patching uuid.uuid4 itself has no effect.
    ids = (uuid.UUID(int=n) for n in itertools.count(1))
    monkeypatch.setattr(Individual._meta.get_field("id"), "_get_default", lambda: next(ids))


@pytest.fixture
def rdi_country_workspace_id() -> str:
    return "cw-rdi-biographic-e2e"


@pytest.fixture
def create_rdi_payload(
    social_program: Program, imported_by_user: User, rdi_country_workspace_id: str
) -> dict[str, Any]:
    return {
        "name": "cw-biographic-dedup-rdi",
        "collect_data_policy": "FULL",
        "program": str(social_program.id),
        "imported_by_email": imported_by_user.email,
        "country_workspace_id": rdi_country_workspace_id,
    }


@pytest.fixture
def push_people_payload(social_program: Program) -> list[dict[str, Any]]:
    # Mirrors testing/fixtures/PEOPLE_E2E_RDI.xlsx, keyed by country_workspace_id.
    people = [
        ("cw-rdi-single", "Jonas", "Becker", "MALE", "1987-03-14", "", ""),
        ("cw-rdi-multi", "Lucia", "Fernandez", "FEMALE", "1993-08-21", "+48600111222", "+48600111333"),
        ("cw-rdi-batch-1", "Amara", "Diallo", "FEMALE", "1999-10-30", "", ""),
        ("cw-rdi-batch-2", "Amara", "Diallo", "FEMALE", "1999-10-30", "", ""),
        ("cw-rdi-mixed", "Pavel", "Novak", "MALE", "1980-01-10", "+48600222333", "+48600222444"),
        ("cw-rdi-mixed-partner", "Dmitri", "Orlov", "MALE", "1980-01-10", "+48600222333", "+48600222444"),
        ("cw-rdi-swallowed", "Fatima", "Rahimi", "FEMALE", "1992-07-04", "", ""),
        ("cw-rdi-unique", "Kenji", "Watanabe", "MALE", "1975-12-12", "", ""),
    ]
    return [
        {
            "country_workspace_id": cw_id,
            "program": str(social_program.id),
            "type": "",
            "country": "AF",
            "residence_status": "IDP",
            "given_name": given_name,
            "family_name": family_name,
            "full_name": f"{given_name} {family_name}",
            "sex": sex,
            "birth_date": birth_date,
            "phone_no": phone_no,
            "phone_no_alternative": phone_no_alternative,
        }
        for cw_id, given_name, family_name, sex, birth_date, phone_no, phone_no_alternative in people
    ]


@pytest.fixture
def hde_biographic_findings() -> list[dict[str, Any]]:
    # Pairs from testing/fixtures/PEOPLE_E2E_RECORDING.json, D6 shape + proximity_to_score (D9).
    pairs = [
        ("cw-rdi-single", "cw-pop-single", 0.95, 0.15),
        ("cw-rdi-multi", "cw-pop-multi-name", 0.90, 0.10),
        ("cw-rdi-multi", "cw-pop-multi-phone", 0.85, 0.05),
        ("cw-rdi-batch-1", "cw-rdi-batch-2", 0.95, 0.15),
        ("cw-rdi-mixed", "cw-pop-mixed", 0.90, 0.10),
        ("cw-rdi-mixed", "cw-rdi-mixed-partner", 0.85, 0.05),
        ("cw-rdi-swallowed", "cw-pop-swallowed-a", 0.95, 0.15),
        ("cw-rdi-swallowed", "cw-pop-swallowed-b", 0.95, 0.15),
    ]
    return [
        {
            "first": {"reference_pk": first},
            "second": {"reference_pk": second},
            "score": score,
            "proximity_to_score": proximity_to_score,
            "status_code": "200",
            "config": "default",
            "updated_at": "2026-10-14T00:00:00Z",
        }
        for first, second, score, proximity_to_score in pairs
    ]


@pytest.fixture
def expected_biographic_tickets() -> list[dict[str, Any]]:
    return [
        {"golden_records_individual": "cw-rdi-single", "possible_duplicates": {"cw-pop-single"}},
        {
            "golden_records_individual": "cw-rdi-multi",
            "possible_duplicates": {"cw-pop-multi-name", "cw-pop-multi-phone"},
        },
        {"golden_records_individual": "cw-rdi-batch-1", "possible_duplicates": {"cw-rdi-batch-2"}},
        {"golden_records_individual": "cw-rdi-mixed", "possible_duplicates": {"cw-pop-mixed", "cw-rdi-mixed-partner"}},
    ]


@pytest.fixture
def expected_rdi_statistics() -> dict[str, int]:
    return {
        "golden_record_duplicates": 4,
        "golden_record_unique": 4,
        "batch_duplicates": 4,
        "batch_unique": 4,
    }


@pytest.fixture
def expected_rdi_individual_statuses() -> dict[str, tuple[str, str]]:
    # country_workspace_id -> (deduplication_golden_record_status, deduplication_batch_status)
    return {
        "cw-rdi-single": (DUPLICATE, UNIQUE_IN_BATCH),
        "cw-rdi-multi": (DUPLICATE, UNIQUE_IN_BATCH),
        "cw-rdi-batch-1": (UNIQUE, DUPLICATE_IN_BATCH),
        "cw-rdi-batch-2": (UNIQUE, DUPLICATE_IN_BATCH),
        "cw-rdi-mixed": (DUPLICATE, DUPLICATE_IN_BATCH),
        "cw-rdi-mixed-partner": (UNIQUE, DUPLICATE_IN_BATCH),
        "cw-rdi-swallowed": (DUPLICATE, UNIQUE_IN_BATCH),
        "cw-rdi-unique": (UNIQUE, UNIQUE_IN_BATCH),
    }


@pytest.fixture
def expected_population_golden_record_statuses() -> dict[str, str]:
    return {
        "cw-pop-single": DUPLICATE,
        "cw-pop-multi-name": DUPLICATE,
        "cw-pop-multi-phone": DUPLICATE,
        "cw-pop-mixed": DUPLICATE,
        "cw-pop-swallowed-a": DUPLICATE,
        "cw-pop-swallowed-b": DUPLICATE,
    }


def test_cw_rdi_complete_with_biographic_findings_creates_grouped_tickets_and_stores_statistics(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    social_program: Program,
    afghanistan_country: Country,
    django_elasticsearch_setup: None,
    create_program_es_index: Any,
    population_open_biographic_ticket: TicketNeedsAdjudicationDetails,
    deterministic_individual_ids: None,
    rdi_country_workspace_id: str,
    create_rdi_payload: dict[str, Any],
    push_people_payload: list[dict[str, Any]],
    hde_biographic_findings: list[dict[str, Any]],
    expected_biographic_tickets: list[dict[str, Any]],
    expected_rdi_statistics: dict[str, int],
    expected_rdi_individual_statuses: dict[str, tuple[str, str]],
    expected_population_golden_record_statuses: dict[str, str],
    django_capture_on_commit_callbacks: Any,
    django_assert_num_queries: Any,
    mock_deduplication_engine_env_vars: None,
    eager_celery: None,
    warm_content_type_cache: None,
) -> None:
    """CW RDI with HDE biographic findings: grouped tickets and batch statistics.

    Setup:
        Population (merged): A, B, C, D, E, F
            A - Jonas Becker (cw-pop-single)
            B - Lucia Fernandez (cw-pop-multi-name)
            C - Halina Wrobel (cw-pop-multi-phone)
            D - Pavel Novak (cw-pop-mixed)
            E, F - Fatima Rahimi (cw-pop-swallowed-a, cw-pop-swallowed-b)
        Existing open biographic ticket: {E: [F]} (E is main, [F] is reported duplicate).

        Incoming RDI: a, b, c, d, e, f, g, h
            a - Jonas Becker (cw-rdi-single)
            b - Lucia Fernandez (cw-rdi-multi)
            c, d - Amara Diallo (cw-rdi-batch-1, cw-rdi-batch-2)
            e - Pavel Novak (cw-rdi-mixed)
            f - Dmitri Orlov (cw-rdi-mixed-partner)
            g - Fatima Rahimi (cw-rdi-swallowed)
            h - Kenji Watanabe (cw-rdi-unique)

        HDE biographic findings: (a, A), (b, B), (b, C), (c, d), (e, D), (e, f), (g, E), (g, F)

    Actions:
        create RDI -> push people a..h -> complete (HDE findings mocked)

    Results:
        Tickets:
            {a: [A]}     - single population duplicate
            {b: [B, C]}  - several population duplicates grouped
            {c: [d]}     - intra-batch pair
            {e: [D, f]}  - population and intra-batch duplicates grouped
            g            - no ticket, swallowed by existing {E: [F]}
            h            - no ticket, no findings
    """
    create_program_es_index(social_program)
    create_resp = token_api_client.post(
        reverse("api:rdi-create", args=[user_business_area.slug]), create_rdi_payload, format="json"
    )
    assert create_resp.status_code == status.HTTP_201_CREATED, str(create_resp.json())
    rdi_id = create_resp.json()["id"]
    push_resp = token_api_client.post(
        reverse("api:rdi-push-people", args=[user_business_area.slug, rdi_id]), push_people_payload, format="json"
    )
    assert push_resp.status_code == status.HTTP_201_CREATED, str(push_resp.json())

    with patch(
        "hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_rdi_biographic_findings",
        return_value=hde_biographic_findings,
    ) as mock_biographic_findings:
        # TODO: set the real count once the CW biographic flow is implemented.
        with django_assert_num_queries(0):
            with django_capture_on_commit_callbacks(execute=True):
                complete_resp = token_api_client.post(
                    reverse("api:rdi-complete", args=[user_business_area.slug, rdi_id]), {}, format="json"
                )

    assert complete_resp.status_code == status.HTTP_200_OK, str(complete_resp.json())
    mock_biographic_findings.assert_called_once_with(rdi_country_workspace_id)
    rdi = RegistrationDataImport.objects.get(id=rdi_id)
    assert rdi.status == RegistrationDataImport.MERGED

    ticket_details = (
        TicketNeedsAdjudicationDetails.objects.filter(ticket__registration_data_import=rdi)
        .select_related("ticket", "golden_records_individual")
        .prefetch_related("possible_duplicates")
    )
    assert {details.ticket.issue_type for details in ticket_details} == {
        GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY
    }
    actual_tickets = sorted(
        (
            {
                "golden_records_individual": details.golden_records_individual.country_workspace_id,
                "possible_duplicates": {
                    individual.country_workspace_id for individual in details.possible_duplicates.all()
                },
            }
            for details in ticket_details
        ),
        key=lambda ticket: ticket["golden_records_individual"],
    )
    assert actual_tickets == sorted(expected_biographic_tickets, key=lambda ticket: ticket["golden_records_individual"])

    assert {field: getattr(rdi, field) for field in expected_rdi_statistics} == expected_rdi_statistics
    assert {
        cw_id: (golden_record_status, batch_status)
        for cw_id, golden_record_status, batch_status in Individual.objects.filter(
            registration_data_import=rdi
        ).values_list("country_workspace_id", "deduplication_golden_record_status", "deduplication_batch_status")
    } == expected_rdi_individual_statuses
    assert (
        dict(
            Individual.objects.filter(country_workspace_id__in=expected_population_golden_record_statuses).values_list(
                "country_workspace_id", "deduplication_golden_record_status"
            )
        )
        == expected_population_golden_record_statuses
    )
