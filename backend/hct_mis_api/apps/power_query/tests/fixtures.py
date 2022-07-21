from django.contrib.contenttypes.models import ContentType

import factory

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.power_query.models import Formatter, Query, Report


class ContentTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ContentType
        django_get_or_create = ("app_label", "model")


class QueryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "Query%s" % x)
    owner = factory.SubFactory(UserFactory, is_superuser=True, is_staff=True)
    target = factory.Iterator(ContentType.objects.filter(app_label="auth", model="permission"))
    code = """result=conn.all()
debug_info={"conn": str(conn.query)}
"""

    class Meta:
        model = Query
        django_get_or_create = ("name",)


class FormatterFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "Formatter%s" % x)
    content_type = "html"

    class Meta:
        model = Formatter
        django_get_or_create = ("name",)


class ReportFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "Report%s" % x)
    query = factory.Iterator(Query.objects.all())
    formatter = factory.Iterator(Formatter.objects.all())
    owner = factory.SubFactory(UserFactory, is_superuser=True, is_staff=True, password="123")

    class Meta:
        model = Report
        django_get_or_create = ("name",)
