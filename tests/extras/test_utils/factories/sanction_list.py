import factory
from factory.django import DjangoModelFactory

from hope.models import (
    SanctionList,
    SanctionListIndividual,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
)


class SanctionListFactory(DjangoModelFactory):
    class Meta:
        model = SanctionList
        django_get_or_create = ("strategy",)

    name = factory.Sequence(lambda n: f"Sanction List {n}")
    strategy = "hope.apps.sanction_list.strategies.un.UNSanctionList"


class SanctionListIndividualFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividual

    sanction_list = factory.SubFactory(SanctionListFactory)
    data_id = factory.Sequence(lambda n: n + 1)
    version_num = 1
    first_name = factory.Sequence(lambda n: f"First{n}")
    full_name = factory.Sequence(lambda n: f"First{n} Last{n}")
    reference_number = factory.Sequence(lambda n: f"REF-{n}")
    list_type = factory.Sequence(lambda n: f"Type {n}")


class SanctionListIndividualDateOfBirthFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividualDateOfBirth

    individual = factory.SubFactory(SanctionListIndividualFactory)


class SanctionListIndividualDocumentFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividualDocument

    individual = factory.SubFactory(SanctionListIndividualFactory)
    document_number = factory.Sequence(lambda n: f"DOC-{n}")
    type_of_document = factory.Sequence(lambda n: f"Type{n}")
