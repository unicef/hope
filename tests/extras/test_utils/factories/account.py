"""Account-related factories."""


from django.contrib.auth import get_user_model
import factory
from factory.django import DjangoModelFactory

from hope.models import AdminAreaLimitedTo, Partner, Role, RoleAssignment

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
    subsystem = "HOPE"


class RoleAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = RoleAssignment
        django_get_or_create = ("user", "partner", "role", "business_area")


class AdminAreaLimitedToFactory(DjangoModelFactory):
    class Meta:
        model = AdminAreaLimitedTo

    @factory.post_generation
    def areas(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.areas.set(extracted)
