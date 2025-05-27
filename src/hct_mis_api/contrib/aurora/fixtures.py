from typing import Any

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.contrib.aurora.models import (Organization, Project,
                                               Registration)

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

    @classmethod
    def _create(cls, target_class: Any, *args: Any, **kwargs: Any) -> Registration:
        created_at = kwargs.pop("created_at", None)
        obj = super()._create(target_class, *args, **kwargs)
        if created_at:
            obj.created_at = created_at
            obj.save()
        return obj


def generate_aurora_test_data() -> None:
    program = Program.objects.get(name="Test Program")
    ukr_org = OrganizationFactory(
        **{
            "source_id": 1,
            "name": "organization_ukraine",
            "slug": "ukraine",
            "business_area": BusinessAreaFactory(name="Ukraine"),
        }
    )

    czech_org = OrganizationFactory(
        **{
            "source_id": 1,
            "name": "organization_czech_republic",
            "slug": "czech-republic",
            "business_area": BusinessAreaFactory(name="Czechia"),
        }
    )
    sri_lanka_org = OrganizationFactory(
        **{
            "source_id": 1,
            "name": "organization_sri_lanka",
            "slug": "sri-lanka",
            "business_area": BusinessAreaFactory(name="Sri Lanka"),
        }
    )
    ukr_project = ProjectFactory(
        **{
            "source_id": 2,
            "organization": ukr_org,
            "programme": program,
            "name": "project_ukraine",
        }
    )
    czech_project = ProjectFactory(
        **{
            "source_id": 2,
            "organization": czech_org,
            "programme": program,
            "name": "project_czech_republic",
        }
    )
    sri_lanka_project = ProjectFactory(
        **{
            "source_id": 2,
            "organization": sri_lanka_org,
            "programme": program,
            "name": "project_sri_lanka",
        }
    )
    RegistrationFactory(
        **{
            "source_id": 2,
            "project": ukr_project,
            "name": "registration_ukraine",
            "slug": "ukraine",
        }
    )
    RegistrationFactory(
        **{
            "source_id": 2,
            "project": czech_project,
            "name": "registration_czech_republic",
            "slug": "czech-republic",
        }
    )
    RegistrationFactory(
        **{
            "source_id": 2,
            "project": sri_lanka_project,
            "name": "registration_sri_lanka",
            "slug": "sri-lanka",
        }
    )
