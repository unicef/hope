from django.test import TestCase, override_settings

from hct_mis_api.apps.power_query.tests.fixtures import (
    ParametrizerFactory,
    QueryFactory,
)


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQuery(TestCase):
    databases = {"default"}

    def test_create_defaults(self) -> None:
        from hct_mis_api.apps.power_query.defaults import create_defaults

        create_defaults()

    def test_parameter(self) -> None:
        p = ParametrizerFactory()
        p.refresh()

    def test_parameter_custom_source(self) -> None:
        from django.contrib.contenttypes.models import ContentType

        from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
        from hct_mis_api.apps.core.models import BusinessArea
        from hct_mis_api.apps.power_query.models import Parametrizer, Query

        ba = BusinessAreaFactory()
        q: Query = QueryFactory(
            target=ContentType.objects.get_for_model(BusinessArea),
            code='result = { "business_area": [ b.slug for b in conn.all()] }',
        )
        p: Parametrizer = ParametrizerFactory(source=q, code="c1", name="", value="")
        p.refresh()
        p.refresh_from_db()
        assert p.value == {"business_area": [ba.slug]}
