import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.aurora.models import Organization, Project, Registration

faker = Faker()


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization
        django_get_or_create = ("name", "slug", "business_area", "source_id")

    name = "UNICEF"
    slug = "unicef"
    source_id = factory.fuzzy.FuzzyInteger(1, 100)
    business_area = factory.SubFactory(BusinessAreaFactory)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project
        django_get_or_create = ("organization", "programme", "name")

    name = factory.LazyFunction(faker.domain_word)
    programme = factory.SubFactory(ProgramFactory)
    organization = factory.SubFactory(OrganizationFactory)
    source_id = factory.fuzzy.FuzzyInteger(1, 100)


class RegistrationFactory(DjangoModelFactory):
    class Meta:
        model = Registration
        django_get_or_create = ("project", "name", "slug")

    slug = "reg-n"
    name = factory.LazyFunction(faker.city)
    project = factory.SubFactory(ProjectFactory)
    source_id = factory.fuzzy.FuzzyInteger(1, 100)
