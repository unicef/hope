from django.urls import reverse

from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.program.fixtures import BeneficiaryGroupFactory
from tests.unit.api.base import HOPEApiTestCase


class BeneficiaryGroupAPITestCase(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        cls.client = APIClient()

        cls.list_url = reverse(
            "api:beneficiary_group:beneficiary_groups-list",
        )
        cls.bg1 = BeneficiaryGroupFactory(name="bg1")
        cls.bg2 = BeneficiaryGroupFactory(name="bg2")

    def test_beneficiary_group_list(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        etag = response.headers["ETAG"]
        self.assertEqual(
            response.json()["results"],
            [
                {
                    "id": str(self.bg1.id),
                    "name": "bg1",
                    "group_label": self.bg1.group_label,
                    "group_label_plural": self.bg1.group_label_plural,
                    "member_label": self.bg1.member_label,
                    "member_label_plural": self.bg1.member_label_plural,
                    "master_detail": self.bg1.master_detail,
                },
                {
                    "id": str(self.bg2.id),
                    "name": "bg2",
                    "group_label": self.bg2.group_label,
                    "group_label_plural": self.bg2.group_label_plural,
                    "member_label": self.bg2.member_label,
                    "member_label_plural": self.bg2.member_label_plural,
                    "master_detail": self.bg2.master_detail,
                },
            ],
        )

        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(response.status_code, 304)

        self.bg1.group_label = "new_group_label"
        self.bg1.save()
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(response.status_code, 200)
        after_edit_etag = response.headers["ETAG"]
        self.assertNotEqual(
            etag,
            after_edit_etag,
        )

        self.bg1.delete()
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=after_edit_etag)
        self.assertEqual(response.status_code, 200)
        after_delete_etag = response.headers["ETAG"]
        self.assertNotEqual(
            after_edit_etag,
            after_delete_etag,
        )
        self.assertNotEqual(
            etag,
            after_delete_etag,
        )
