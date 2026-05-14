import os
from typing import Any
from unittest import mock
from unittest.mock import patch
import uuid

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.grievance.models import TicketNeedsAdjudicationDetails
from hope.models import (
    BusinessArea,
    Country,
    DataCollectingType,
    DeduplicationEngineSimilarityPair,
    DocumentType,
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
def mock_deduplication_engine_env_vars() -> Any:
    with mock.patch.dict(
        os.environ,
        {
            "DEDUPLICATION_ENGINE_API_KEY": "TEST",
            "DEDUPLICATION_ENGINE_API_URL": "TEST/",
        },
    ):
        yield


@pytest.fixture
def cw_dedup_eager_setup(user_business_area: BusinessArea) -> None:
    from hope.apps.core.celery import app as celery_app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True

    user_business_area.postpone_deduplication = True
    user_business_area.save(update_fields=["postpone_deduplication"])


@pytest.fixture
def cw_correlation_id() -> str:
    return f"cw-e2e-lax-{uuid.uuid4()}"


@pytest.fixture
def cw_individual_ids() -> dict[str, str]:
    return {"A": "cw-ind-A", "B": "cw-ind-B", "C": "cw-ind-C"}


@pytest.fixture
def cw_findings(cw_individual_ids: dict[str, str]) -> list[dict]:
    return [
        {
            "first": {"reference_pk": cw_individual_ids["A"]},
            "second": {"reference_pk": cw_individual_ids["B"]},
            "score": 0.95,
            "status_code": "200",
            "config": "default",
            "updated_at": "2026-05-14T00:00:00Z",
        },
    ]


def _create_rdi(
    token_api_client: APIClient,
    business_area: BusinessArea,
    program: Program,
    imported_by: User,
    correlation_id: str,
    name: str,
) -> str:
    create_url = reverse("api:rdi-create", args=[business_area.slug])
    resp = token_api_client.post(
        create_url,
        {
            "name": name,
            "collect_data_policy": "FULL",
            "program": str(program.id),
            "imported_by_email": imported_by.email,
            "correlation_id": correlation_id,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, str(resp.json())
    return resp.json()["id"]


def _complete_rdi(
    token_api_client: APIClient,
    business_area: BusinessArea,
    rdi_id: str,
    cw_findings: list[dict],
    cw_correlation_id: str,
    django_capture_on_commit_callbacks: Any,
    django_assert_num_queries: Any,
    expected_queries: int,
) -> None:
    complete_url = reverse("api:rdi-complete", args=[business_area.slug, rdi_id])
    with (
        patch(
            "hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_group_findings",
            return_value=cw_findings,
        ) as mock_findings,
        patch(
            "hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.approve_group",
            return_value=({}, 200),
        ) as mock_approve,
    ):
        with django_assert_num_queries(expected_queries):
            with django_capture_on_commit_callbacks(execute=True):
                resp = token_api_client.post(complete_url, {}, format="json")

    assert resp.status_code == status.HTTP_200_OK, str(resp.json())
    mock_findings.assert_called_once_with(cw_correlation_id)
    mock_approve.assert_called_once_with(cw_correlation_id)


def _individual_payload(individual_id: str, country_workspace_id: str, document_type_key: str) -> dict[str, Any]:
    return {
        "individual_id": individual_id,
        "full_name": f"Person {individual_id}",
        "given_name": f"Given{individual_id}",
        "family_name": f"Family{individual_id}",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "documents": [
            {
                "type": document_type_key,
                "country": "AF",
                "document_number": f"DOC-{individual_id}",
                "issuance_date": "2020-01-01",
                "expiry_date": "2030-01-01",
            }
        ],
        "country_workspace_id": country_workspace_id,
    }


def test_cw_lax_auto_merges_with_duplicate_ticket(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    imported_by_user: User,
    afghanistan_country: Country,
    birth_certificate_doc_type: DocumentType,
    django_elasticsearch_setup: None,
    create_program_es_index: Any,
    cw_correlation_id: str,
    cw_individual_ids: dict[str, str],
    cw_findings: list[dict],
    django_capture_on_commit_callbacks: Any,
    django_assert_num_queries: Any,
    mock_deduplication_engine_env_vars: Any,
    cw_dedup_eager_setup: None,
) -> None:
    create_program_es_index(program)

    rdi_id = _create_rdi(
        token_api_client=token_api_client,
        business_area=user_business_area,
        program=program,
        imported_by=imported_by_user,
        correlation_id=cw_correlation_id,
        name="cw-e2e-lax-rdi",
    )

    rdi = RegistrationDataImport.objects.get(id=rdi_id)
    assert rdi.status == RegistrationDataImport.LOADING

    push_indiv_url = reverse("api:rdi-push-lax-individuals", args=[user_business_area.slug, rdi_id])
    indiv_resp = token_api_client.post(
        push_indiv_url,
        [
            _individual_payload("IND_A", cw_individual_ids["A"], birth_certificate_doc_type.key),
            _individual_payload("IND_B", cw_individual_ids["B"], birth_certificate_doc_type.key),
            _individual_payload("IND_C", cw_individual_ids["C"], birth_certificate_doc_type.key),
        ],
        format="json",
    )
    assert indiv_resp.status_code == status.HTTP_201_CREATED, str(indiv_resp.json())
    assert indiv_resp.data["accepted"] == 3
    id_map = indiv_resp.data["individual_id_mapping"]
    hoh_unicef_id = id_map["IND_A"]
    member_b_unicef_id = id_map["IND_B"]
    member_c_unicef_id = id_map["IND_C"]

    push_hh_url = reverse("api:rdi-push-lax-households", args=[user_business_area.slug, rdi_id])
    hh_resp = token_api_client.post(
        push_hh_url,
        [
            {
                "country": "AF",
                "country_origin": "AF",
                "size": 3,
                "consent_sharing": ["UNICEF"],
                "village": "CW Village",
                "head_of_household_id": hoh_unicef_id,
                "primary_collector_id": hoh_unicef_id,
                "members": [hoh_unicef_id, member_b_unicef_id, member_c_unicef_id],
            }
        ],
        format="json",
    )
    assert hh_resp.status_code == status.HTTP_201_CREATED, str(hh_resp.json())
    assert hh_resp.data["accepted"] == 1

    _complete_rdi(
        token_api_client=token_api_client,
        business_area=user_business_area,
        rdi_id=rdi_id,
        cw_findings=cw_findings,
        cw_correlation_id=cw_correlation_id,
        django_capture_on_commit_callbacks=django_capture_on_commit_callbacks,
        django_assert_num_queries=django_assert_num_queries,
        expected_queries=174,
    )

    rdi = RegistrationDataImport.objects.get(id=rdi_id)
    assert rdi.status == RegistrationDataImport.MERGED

    pairs = DeduplicationEngineSimilarityPair.objects.filter(program=program)
    assert pairs.count() == 1
    pair = pairs.get()
    paired_cw_ids = {pair.individual1.country_workspace_id, pair.individual2.country_workspace_id}
    assert paired_cw_ids == {cw_individual_ids["A"], cw_individual_ids["B"]}

    merged = Individual.objects.filter(registration_data_import=rdi)
    assert set(merged.values_list("country_workspace_id", flat=True)) == set(cw_individual_ids.values())

    ind_a = merged.get(country_workspace_id=cw_individual_ids["A"])
    ind_b = merged.get(country_workspace_id=cw_individual_ids["B"])
    ind_c = merged.get(country_workspace_id=cw_individual_ids["C"])

    tickets_for_pair = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual__in=[ind_a, ind_b])
    assert tickets_for_pair.count() == 1
    ticket = tickets_for_pair.get()
    involved_ids = {
        ticket.golden_records_individual_id,
        *ticket.possible_duplicates.values_list("id", flat=True),
    }
    assert involved_ids == {ind_a.id, ind_b.id}
    assert ticket.is_multiple_duplicates_version is True

    tickets_for_c = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual=ind_c)
    assert not tickets_for_c.exists()


@pytest.fixture
def social_program(business_area: BusinessArea) -> Program:
    dct = DataCollectingTypeFactory(
        label="Full",
        code="full",
        type=DataCollectingType.Type.SOCIAL.value,
    )
    dct.limit_to.add(business_area)
    beneficiary_group = BeneficiaryGroupFactory(master_detail=False)
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
        biometric_deduplication_enabled=True,
    )


def _person_payload(name: str, country_workspace_id: str, program: Program) -> dict[str, Any]:
    return {
        "residence_status": "IDP",
        "village": "village1",
        "country": "AF",
        "full_name": name,
        "birth_date": "2000-01-01",
        "sex": "MALE",
        "type": "",
        "program": str(program.id),
        "country_workspace_id": country_workspace_id,
    }


def test_cw_social_workers_auto_merges_with_duplicate_ticket(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    social_program: Program,
    imported_by_user: User,
    afghanistan_country: Country,
    django_elasticsearch_setup: None,
    create_program_es_index: Any,
    cw_correlation_id: str,
    cw_individual_ids: dict[str, str],
    cw_findings: list[dict],
    django_capture_on_commit_callbacks: Any,
    django_assert_num_queries: Any,
    mock_deduplication_engine_env_vars: Any,
    cw_dedup_eager_setup: None,
) -> None:
    create_program_es_index(social_program)

    rdi_id = _create_rdi(
        token_api_client=token_api_client,
        business_area=user_business_area,
        program=social_program,
        imported_by=imported_by_user,
        correlation_id=cw_correlation_id,
        name="cw-e2e-people-rdi",
    )

    rdi = RegistrationDataImport.objects.get(id=rdi_id)
    assert rdi.status == RegistrationDataImport.LOADING

    push_people_url = reverse("api:rdi-push-people", args=[user_business_area.slug, rdi_id])
    people_resp = token_api_client.post(
        push_people_url,
        [
            _person_payload("Person A", cw_individual_ids["A"], social_program),
            _person_payload("Person B", cw_individual_ids["B"], social_program),
            _person_payload("Person C", cw_individual_ids["C"], social_program),
        ],
        format="json",
    )
    assert people_resp.status_code == status.HTTP_201_CREATED, str(people_resp.json())

    _complete_rdi(
        token_api_client=token_api_client,
        business_area=user_business_area,
        rdi_id=rdi_id,
        cw_findings=cw_findings,
        cw_correlation_id=cw_correlation_id,
        django_capture_on_commit_callbacks=django_capture_on_commit_callbacks,
        django_assert_num_queries=django_assert_num_queries,
        expected_queries=171,
    )

    rdi = RegistrationDataImport.objects.get(id=rdi_id)
    assert rdi.status == RegistrationDataImport.MERGED

    pairs = DeduplicationEngineSimilarityPair.objects.filter(program=social_program)
    assert pairs.count() == 1
    pair = pairs.get()
    paired_cw_ids = {pair.individual1.country_workspace_id, pair.individual2.country_workspace_id}
    assert paired_cw_ids == {cw_individual_ids["A"], cw_individual_ids["B"]}

    merged = Individual.objects.filter(registration_data_import=rdi)
    assert set(merged.values_list("country_workspace_id", flat=True)) == set(cw_individual_ids.values())

    ind_a = merged.get(country_workspace_id=cw_individual_ids["A"])
    ind_b = merged.get(country_workspace_id=cw_individual_ids["B"])
    ind_c = merged.get(country_workspace_id=cw_individual_ids["C"])

    tickets_for_pair = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual__in=[ind_a, ind_b])
    assert tickets_for_pair.count() == 1
    ticket = tickets_for_pair.get()
    involved_ids = {
        ticket.golden_records_individual_id,
        *ticket.possible_duplicates.values_list("id", flat=True),
    }
    assert involved_ids == {ind_a.id, ind_b.id}
    assert ticket.is_multiple_duplicates_version is True

    tickets_for_c = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual=ind_c)
    assert not tickets_for_c.exists()
