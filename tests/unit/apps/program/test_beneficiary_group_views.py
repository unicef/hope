from typing import Any

from django.core.cache import cache
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import BeneficiaryGroupFactory

pytestmark = pytest.mark.django_db


class TestBeneficiaryGroupViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.user = UserFactory()
        self.client = api_client(self.user)
        self.afghanistan = create_afghanistan()

        self.list_url = reverse("api:programs:beneficiary-groups-list")
        self.beneficiary_group1 = BeneficiaryGroupFactory(name="Household")
        self.beneficiary_group2 = BeneficiaryGroupFactory(name="Social Workers")

    def test_list_beneficiary_group(self) -> None:
        cache.clear()
        response = self.client.get(self.list_url)
        self.beneficiary_group1.refresh_from_db()
        self.beneficiary_group2.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
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
        assert response.status_code == status.HTTP_200_OK
        etag = response.headers["ETAG"]

        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=etag)
        assert response.status_code == status.HTTP_304_NOT_MODIFIED
        etag_after_cache = response.headers["ETAG"]

        self.beneficiary_group1.group_label = "new_group_label"
        self.beneficiary_group1.save()
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=etag)
        assert response.status_code == status.HTTP_200_OK
        after_edit_etag = response.headers["ETAG"]
        assert etag_after_cache != after_edit_etag

        beneficiary_group3 = BeneficiaryGroupFactory(name="Other `BG")
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=after_edit_etag)
        assert response.status_code == status.HTTP_200_OK
        after_create_etag = response.headers["ETAG"]
        assert after_edit_etag != after_create_etag

        beneficiary_group3.delete()
        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=after_create_etag)
        assert response.status_code == status.HTTP_200_OK
        after_delete_etag = response.headers["ETAG"]
        assert after_create_etag != after_delete_etag

        response = self.client.get(self.list_url, HTTP_IF_NONE_MATCH=after_delete_etag)
        assert response.status_code == status.HTTP_304_NOT_MODIFIED
        etag_after_cache_2 = response.headers["ETAG"]
        assert etag_after_cache_2 == after_delete_etag
