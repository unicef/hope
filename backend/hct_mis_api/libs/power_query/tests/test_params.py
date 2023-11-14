from django.test import override_settings

from power_query.fixtures import ParametrizerFactory, QueryFactory

from hct_mis_api.apps.core.base_test_case import DefaultTestCase


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQuery(DefaultTestCase):
    databases = {"default"}

    def test_create_defaults(self) -> None:
        from hct_mis_api.libs.power_query.defaults import create_defaults

        create_defaults()

    def test_parameter(self) -> None:
        p = ParametrizerFactory()
        p.refresh()

    def test_parameter_custom_source(self) -> None:
        from django.contrib.contenttypes.models import ContentType

        from power_query.models import Parametrizer, Query

        from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
        from hct_mis_api.apps.core.models import BusinessArea

        ba = BusinessAreaFactory()
        q: Query = QueryFactory(
            target=ContentType.objects.get_for_model(BusinessArea),
            code='result = { "business_area": [ b.slug for b in conn.all()] }',
        )
        p: Parametrizer = ParametrizerFactory(source=q, code="c1", name="", value="")
        p.refresh()
        p.refresh_from_db()
        assert p.value == {"business_area": [ba.slug]}
