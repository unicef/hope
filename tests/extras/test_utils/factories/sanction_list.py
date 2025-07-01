import factory
from factory.django import DjangoModelFactory

from hct_mis_api.apps.sanction_list.models import SanctionList


class SanctionListFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Sanction List {n}")
    strategy = "hct_mis_api.apps.sanction_list.strategies.un.UNSanctionList"

    class Meta:
        model = SanctionList
        django_get_or_create = ("name",)
