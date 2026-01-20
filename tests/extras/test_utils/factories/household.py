"""Household-related factories."""

from datetime import date

from django.utils import timezone
import factory
from factory.django import DjangoModelFactory

from hope.apps.household.const import ROLE_PRIMARY
from hope.models import Household, Individual, IndividualRoleInHousehold


class IndividualFactory(DjangoModelFactory):
    class Meta:
        model = Individual

    full_name = factory.Sequence(lambda n: f"Person {n}")
    sex = "MALE"
    birth_date = date(1990, 1, 1)
    first_registration_date = factory.LazyFunction(date.today)
    last_registration_date = factory.LazyFunction(date.today)


class HouseholdFactory(DjangoModelFactory):
    class Meta:
        model = Household

    first_registration_date = factory.LazyFunction(timezone.now)
    last_registration_date = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def head_of_household(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # Use provided individual
            self.head_of_household = extracted
            individual = extracted
        else:
            # Create new individual as head of household
            individual = IndividualFactory(
                household=self,
                business_area=self.business_area,
                program=self.program,
                registration_data_import=self.registration_data_import,
            )
            self.head_of_household = individual

        self.save()

        # Create primary collector role
        IndividualRoleInHouseholdFactory(
            household=self,
            individual=individual,
        )


class IndividualRoleInHouseholdFactory(DjangoModelFactory):
    class Meta:
        model = IndividualRoleInHousehold

    role = ROLE_PRIMARY
