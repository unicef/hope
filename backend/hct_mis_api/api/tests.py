from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.household.models import HEAD, MALE, ROLE_PRIMARY, SON_DAUGHTER
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
)


class UploadRDITests(APITestCase):
    databases = ["default", "registration_datahub"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        BusinessAreaFactory(name="Afghanistan")

    def test_upload_single_household(self):
        url = reverse("api:rdi-upload", args=["afghanistan"])
        data = {
            "name": "aaaa",
            "number_of_households": 1,
            "number_of_individuals": 1,
            "households": [
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
                    "members": [
                        {
                            "relationship": HEAD,
                            "role": ROLE_PRIMARY,
                            "full_name": "Jhon Doe",
                            "birth_date": "2000-01-01",
                            "sex": "MALE",
                        },
                        {
                            "relationship": SON_DAUGHTER,
                            "full_name": "Mary Doe",
                            "birth_date": "2000-01-01",
                            "role": "",
                            "sex": "FEMALE",
                        },
                    ],
                    "collect_individual_data": "FULL",
                    "size": 1,
                }
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        hoh = ImportedIndividual.objects.filter(birth_date="2000-01-01", full_name="Jhon Doe", sex=MALE).first()

        self.assertTrue(hoh)
        hh: ImportedHousehold = hoh.household
        self.assertEqual(hoh.household.village, "village1")
        # can we test this ?
        # self.assertEqual(hoh.household.primary_collector, hoh)
        # self.assertFalse(hoh.household.alternate_collector)
        members = hh.individuals.all()
        self.assertEqual(len(members), 2)
