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
            "api:beneficiary-group:beneficiary-group-list",
        )
        cls.beneficiary_group1 = BeneficiaryGroupFactory(name="Household")
        cls.beneficiary_group2 = BeneficiaryGroupFactory(name="Social Workers")

    def test_list_beneficiary_group(self) -> None:
        response = self.client.get(self.list_url)
        self.beneficiary_group1.refresh_from_db()
        self.beneficiary_group2.refresh_from_db()
        assert response.status_code == 200
        assert {
            "id": str(self.beneficiary_group1.id),
            "name": "Household",
            "group_label": self.beneficiary_group1.group_label,
            "group_label_plural": self.beneficiary_group1.group_label_plural,
            "member_label": self.beneficiary_group1.member_label,
            "member_label_plural": self.beneficiary_group1.member_label_plural,
            "master_detail": self.beneficiary_group1.master_detail,
        } in response.json()["results"]
        assert {
            "id": str(self.beneficiary_group2.id),
            "name": "Social Workers",
            "group_label": self.beneficiary_group2.group_label,
            "group_label_plural": self.beneficiary_group2.group_label_plural,
            "member_label": self.beneficiary_group2.member_label,
            "member_label_plural": self.beneficiary_group2.member_label_plural,
            "master_detail": self.beneficiary_group2.master_detail,
        } in response.json()["results"]

    def test_list_beneficiary_group_caching(self) -> None:
        response = self.client.get(self.list_url)
        assert response.status_code == 200
        etag = response.headers["ETAG"]

        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=etag)
        assert response.status_code == 304

        self.beneficiary_group1.group_label = "new_group_label"
        self.beneficiary_group1.save()
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=etag)
        assert response.status_code == 200
        after_edit_etag = response.headers["ETAG"]
        assert etag != after_edit_etag

        beneficiary_group3 = BeneficiaryGroupFactory(name="Other `BG")
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=after_edit_etag)
        assert response.status_code == 200
        after_create_etag = response.headers["ETAG"]
        assert after_edit_etag != after_create_etag

        beneficiary_group3.delete()
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=after_create_etag)
        assert response.status_code == 200
        after_delete_etag = response.headers["ETAG"]
        assert after_create_etag != after_delete_etag
        assert etag != after_delete_etag

        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=after_delete_etag)
        assert response.status_code == 304
