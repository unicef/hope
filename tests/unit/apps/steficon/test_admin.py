from uuid import uuid4

from django.urls import reverse

import pytest

from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.steficon.admin import AutocompleteWidget

pytestmark = pytest.mark.django_db()


class TestAutocompleteWidget:
    def test_get_url_without_business_area(self) -> None:
        widget = AutocompleteWidget(model=Program, admin_site="admin")
        expected_url = reverse("admin:autocomplete")
        assert widget.get_url() == expected_url

    def test_get_url_with_business_area(self) -> None:
        business_area_id = uuid4()
        widget = AutocompleteWidget(model=Program, admin_site="admin", business_area=business_area_id)
        expected_url = f"{reverse('admin:autocomplete')}?business_area={business_area_id}"
        assert widget.get_url() == expected_url

    def test_get_context_without_business_area(self) -> None:
        widget = AutocompleteWidget(model=Program, admin_site="admin")
        mock_attrs = {"class": "test-class"}
        context = widget.get_context("program", "test_value", mock_attrs)

        assert context["widget"]["query_string"] == ""
        assert context["widget"]["url"] == reverse("admin:autocomplete")
        assert context["widget"]["target_opts"]["app_label"] == "program"
        assert context["widget"]["target_opts"]["model_name"] == "program"
        assert context["widget"]["target_opts"]["target_field"] == "id"
        assert context["widget"]["name"] == "program"
        assert context["widget"]["attrs"]["class"] == "test-class"

    def test_get_context_with_business_area(self) -> None:
        business_area_id = uuid4()
        widget = AutocompleteWidget(model=Program, admin_site="admin", business_area=business_area_id)
        mock_attrs = {"class": "test-class"}
        context = widget.get_context("program", "test_value", mock_attrs)

        assert context["widget"]["query_string"] == f"business_area__exact={business_area_id}"
        assert context["widget"]["url"] == f"{reverse('admin:autocomplete')}?business_area={business_area_id}"
