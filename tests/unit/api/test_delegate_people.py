from typing import List
from uuid import UUID

from django.core.management import call_command

from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
    DocumentType,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from tests.unit.api.base import HOPEApiTestCase


class TestDelegatePeople(HOPEApiTestCase):
    user_permissions = [Grant.API_RDI_UPLOAD]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")
        DocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE], label="--"
        )
        data_collecting_type = DataCollectingTypeFactory(
            label="Full",
            code="full",
            weight=1,
            business_areas=[cls.business_area],
            type=DataCollectingType.Type.SOCIAL.value,
        )
        cls.program = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area, data_collecting_type=data_collecting_type
        )
        cls.rdi: RegistrationDataImport = RegistrationDataImport.objects.create(
            business_area=cls.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=cls.program,
        )

        cls.url = reverse("api:rdi-delegate-people", args=[cls.business_area.slug, str(cls.rdi.id)])

    def test_external_collector(self) -> None:
        people_ids = self._create_people()
        households_count = PendingHousehold.objects.filter(registration_data_import=self.rdi).count()
        individuals_count = PendingIndividual.objects.filter(registration_data_import=self.rdi).count()
        self.assertEqual(households_count, 2)
        self.assertEqual(individuals_count, 3)

        data = {"delegates": [{"delegate_id": people_ids[2], "delegated_for": [people_ids[1]]}]}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, str(response.json()))
        data = response.json()
        self.assertEqual(data["updated"], 1)

        hh1 = PendingHousehold.objects.get(registration_data_import=self.rdi, village="village1")
        hh2 = PendingHousehold.objects.get(registration_data_import=self.rdi, village="village2")

        self.assertEqual(hh1.primary_collector.full_name, "John Doe")
        self.assertEqual(hh2.primary_collector.full_name, "Jack Jones")

    def _create_people(self) -> List[UUID]:
        data = [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "collect_individual_data": COLLECT_TYPE_FULL,
                "full_name": "John Doe",
                "birth_date": "2000-01-01",
                "sex": "MALE",
                "type": "",
                "documents": [
                    {
                        "document_number": "10",
                        "image": "",
                        "doc_date": "2010-01-01",
                        "country": "AF",
                        "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                    }
                ],
            },
            {
                "residence_status": "IDP",
                "village": "village2",
                "country": "AF",
                "collect_individual_data": COLLECT_TYPE_FULL,
                "full_name": "Mary Doe",
                "birth_date": "1990-01-01",
                "sex": "FEMALE",
                "type": "",
            },
            {
                "residence_status": "IDP",
                "village": "village3",
                "country": "AF",
                "collect_individual_data": COLLECT_TYPE_FULL,
                "full_name": "Jack Jones",
                "birth_date": "1980-01-01",
                "sex": "MALE",
                "type": NON_BENEFICIARY,
            },
        ]
        url = reverse("api:rdi-push-people", args=[self.business_area.slug, str(self.rdi.id)])
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        response_json = response.json()
        return response_json["people"]
