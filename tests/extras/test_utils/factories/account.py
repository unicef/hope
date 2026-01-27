"""Account-related factories."""

from typing import Any

from django.contrib.auth import get_user_model
import factory
from factory.django import DjangoModelFactory

from hope.models import AdminAreaLimitedTo, Partner, Role, RoleAssignment

from .core import BusinessAreaFactory
from .program import ProgramFactory

User = get_user_model()


class PartnerFactory(DjangoModelFactory):
    class Meta:
        model = Partner
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Partner {n}")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username", "email")

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    partner = factory.SubFactory(PartnerFactory)


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name", "subsystem")

    name = factory.Sequence(lambda n: f"Role {n}")
    subsystem = Role.HOPE


class RoleAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = RoleAssignment
        django_get_or_create = ("user", "partner", "role", "business_area")

    user = None
    partner = None
    role = factory.SubFactory(RoleFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> RoleAssignment:
        partner = kwargs.get("partner")
        user = kwargs.get("user")
        if not user and not partner:
            user = UserFactory()
            kwargs["user"] = user
        if partner:
            partner.allowed_business_areas.add(kwargs["business_area"])
        return super()._create(model_class, *args, **kwargs)


class AdminAreaLimitedToFactory(DjangoModelFactory):
    class Meta:
        model = AdminAreaLimitedTo

    partner = factory.SubFactory(PartnerFactory)
    program = factory.SubFactory(ProgramFactory)

    @factory.post_generation
    def areas(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.areas.set(extracted)
