"""Aurora-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.contrib.aurora.models import Organization, Project, Registration


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    source_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Organization {n}")
    slug = factory.Sequence(lambda n: f"organization-{n}")
    business_area = None


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    source_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Project {n}")
    organization = factory.SubFactory(OrganizationFactory)
    programme = None


class RegistrationFactory(DjangoModelFactory):
    class Meta:
        model = Registration

    source_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Registration {n}")
    slug = factory.Sequence(lambda n: f"registration-{n}")
    project = factory.SubFactory(ProjectFactory)
    rdi_parser = None
