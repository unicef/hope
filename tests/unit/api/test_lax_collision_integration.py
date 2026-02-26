import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    APITokenFactory,
    BusinessAreaFactory,
    CountryFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.household.const import REMOVED_BY_COLLISION
from hope.apps.program.collision_detectors import IdentificationKeyCollisionDetector
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.models import Household, Individual, Program, RegistrationDataImport
from hope.models.utils import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db):
    ba = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    ba.postpone_deduplication = True
    ba.save(update_fields=["postpone_deduplication"])
    return ba


@pytest.fixture
def afghanistan_country(db):
    return CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )


@pytest.fixture
def collision_program(business_area):
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
    )
    program.collision_detector = IdentificationKeyCollisionDetector
    program.save(update_fields=["collision_detector"])
    return program


@pytest.fixture
def lax_api_client(business_area):
    user = UserFactory()
    permissions = [Grant.API_RDI_CREATE, Grant.API_RDI_UPLOAD]
    role = RoleFactory(permissions=[p.name for p in permissions])
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)
    token = APITokenFactory(
        user=user,
        grants=[p.name for p in permissions],
    )
    token.valid_for.set([business_area])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client


def test_full_lax_import_merge_collision_flow(
    lax_api_client, business_area, afghanistan_country, collision_program, mock_elasticsearch
):
    # ==== First import — create golden record ====
    rdi1 = RegistrationDataImportFactory(
        business_area=business_area,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.LOADING,
        program=collision_program,
    )

    ind_url = reverse("api:rdi-push-lax-individuals", args=[business_area.slug, str(rdi1.id)])
    resp = lax_api_client.post(
        ind_url,
        [
            {
                "individual_id": "EXT-IND-001",
                "full_name": "Alice Smith",
                "given_name": "Alice",
                "family_name": "Smith",
                "birth_date": "1990-01-01",
                "sex": "FEMALE",
                "phone_no": "+48609111222",
                "identification_key": "IND-KEY-001",
            },
            {
                "individual_id": "EXT-IND-002",
                "full_name": "Bob Johnson",
                "given_name": "Bob",
                "family_name": "Johnson",
                "birth_date": "1995-06-15",
                "sex": "MALE",
                "phone_no": "+48500444555",
                "identification_key": "IND-KEY-002",
            },
        ],
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    assert resp.data["accepted"] == 2
    hoh_uid = resp.data["individual_id_mapping"]["EXT-IND-001"]
    member_uid = resp.data["individual_id_mapping"]["EXT-IND-002"]

    hh_url = reverse("api:rdi-push-lax-households", args=[business_area.slug, str(rdi1.id)])
    resp = lax_api_client.post(
        hh_url,
        [
            {
                "country": "AF",
                "size": 2,
                "village": "Village Alpha",
                "address": "Address One",
                "head_of_household": hoh_uid,
                "primary_collector": hoh_uid,
                "members": [hoh_uid, member_uid],
                "identification_key": "HH-KEY-001",
            },
        ],
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    assert resp.data["accepted"] == 1

    rdi1.status = RegistrationDataImport.IN_REVIEW
    rdi1.save(update_fields=["status"])
    RdiMergeTask().execute(str(rdi1.id))

    rdi1.refresh_from_db()
    assert rdi1.status == RegistrationDataImport.MERGED
    assert Household.objects.filter(program=collision_program).count() == 1
    assert Individual.objects.filter(program=collision_program).count() == 2

    merged_hh = Household.objects.get(program=collision_program)
    assert merged_hh.identification_key == "HH-KEY-001"
    assert merged_hh.village == "Village Alpha"
    assert merged_hh.size == 2

    # ==== Second import — collision ====
    rdi2 = RegistrationDataImportFactory(
        business_area=business_area,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.LOADING,
        program=collision_program,
    )

    ind_url = reverse("api:rdi-push-lax-individuals", args=[business_area.slug, str(rdi2.id)])
    resp = lax_api_client.post(
        ind_url,
        [
            {
                "individual_id": "EXT-IND-002-V2",
                "full_name": "Bob Johnson Updated",
                "given_name": "Bobby",
                "family_name": "Johnson",
                "birth_date": "1995-06-15",
                "sex": "MALE",
                "phone_no": "+48601999888",
                "identification_key": "IND-KEY-002",
            },
            {
                "individual_id": "EXT-IND-003",
                "full_name": "Charlie Brown",
                "given_name": "Charlie",
                "family_name": "Brown",
                "birth_date": "2000-03-20",
                "sex": "MALE",
                "phone_no": "+48512345678",
                "identification_key": "IND-KEY-003",
            },
        ],
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    assert resp.data["accepted"] == 2
    hoh2_uid = resp.data["individual_id_mapping"]["EXT-IND-002-V2"]
    member2_uid = resp.data["individual_id_mapping"]["EXT-IND-003"]

    hh_url = reverse("api:rdi-push-lax-households", args=[business_area.slug, str(rdi2.id)])
    resp = lax_api_client.post(
        hh_url,
        [
            {
                "country": "AF",
                "size": 5,
                "village": "Village Beta",
                "address": "Address Two",
                "head_of_household": hoh2_uid,
                "primary_collector": hoh2_uid,
                "members": [hoh2_uid, member2_uid],
                "identification_key": "HH-KEY-001",
            },
        ],
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    assert resp.data["accepted"] == 1

    rdi2.status = RegistrationDataImport.IN_REVIEW
    rdi2.save(update_fields=["status"])
    RdiMergeTask().execute(str(rdi2.id))

    # ==== Verify collision results ====
    rdi2.refresh_from_db()
    assert rdi2.status == RegistrationDataImport.MERGED
    assert Household.objects.filter(program=collision_program).count() == 1

    merged_hh.refresh_from_db()
    assert merged_hh.size == 5
    assert merged_hh.village == "Village Beta"
    assert merged_hh.address == "Address Two"
    assert rdi2 in merged_hh.extra_rdis.all()

    ind_002 = Individual.objects.get(program=collision_program, identification_key="IND-KEY-002")
    assert ind_002.full_name == "Bob Johnson Updated"
    assert ind_002.given_name == "Bobby"
    assert ind_002.phone_no == "+48601999888"

    ind_003 = Individual.objects.get(program=collision_program, identification_key="IND-KEY-003")
    assert ind_003.household == merged_hh
    assert ind_003.full_name == "Charlie Brown"

    ind_001 = Individual.all_objects.get(program=collision_program, identification_key="IND-KEY-001")
    assert ind_001.withdrawn is True
    assert ind_001.relationship == REMOVED_BY_COLLISION
    assert "removed_by_collision_detector" in ind_001.internal_data
