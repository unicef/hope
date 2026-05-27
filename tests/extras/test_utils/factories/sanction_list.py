"""Sanction list-related factories."""

from datetime import date

from django.core.files.base import ContentFile
import factory
from factory.django import DjangoModelFactory

from hope.models import (
    SanctionList,
    SanctionListIndividual,
    SanctionListIndividualAliasName,
    SanctionListIndividualCountries,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
    SanctionListIndividualNationalities,
    UploadedXLSXFile,
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
    date = factory.LazyFunction(date.today)


class SanctionListIndividualDocumentFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividualDocument

    individual = factory.SubFactory(SanctionListIndividualFactory)
    document_number = factory.Sequence(lambda n: f"DOC-{n}")
    type_of_document = factory.Sequence(lambda n: f"Type{n}")


class SanctionListIndividualCountriesFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividualCountries

    individual = factory.SubFactory(SanctionListIndividualFactory)


class SanctionListIndividualNationalitiesFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividualNationalities

    individual = factory.SubFactory(SanctionListIndividualFactory)


class SanctionListIndividualAliasNameFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividualAliasName

    individual = factory.SubFactory(SanctionListIndividualFactory)
    name = factory.Sequence(lambda n: f"Alias Name {n}")


class UploadedXLSXFileFactory(DjangoModelFactory):
    class Meta:
        model = UploadedXLSXFile

    file = factory.LazyFunction(lambda: ContentFile(b"", name="test.xlsx"))
    associated_email = factory.Sequence(lambda n: f"user{n}@example.com")
