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
    rdi_merge_status = "MERGED"


class HouseholdFactory(DjangoModelFactory):
    class Meta:
        model = Household

    first_registration_date = factory.LazyFunction(timezone.now)
    last_registration_date = factory.LazyFunction(timezone.now)
    rdi_merge_status = "MERGED"

    @factory.post_generation
    def head_of_household(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.head_of_household = extracted
            individual = extracted
            # Update the individual's household reference if not already set
            if individual.household_id != self.pk:
                individual.household = self
                individual.save(update_fields=["household"])
        else:
            # Import here to avoid circular import
            from .registration_data import RegistrationDataImportFactory

            # Use existing registration_data_import or create one
            rdi = self.registration_data_import
            if rdi is None:
                rdi = RegistrationDataImportFactory(
                    business_area=self.business_area,
                    program=self.program,
                )
                self.registration_data_import = rdi

            individual = IndividualFactory(
                household=self,
                business_area=self.business_area,
                program=self.program,
                registration_data_import=rdi,
                rdi_merge_status=self.rdi_merge_status,
            )
            self.head_of_household = individual

        self.save()

        IndividualRoleInHouseholdFactory(household=self, individual=individual, rdi_merge_status=self.rdi_merge_status)


class IndividualRoleInHouseholdFactory(DjangoModelFactory):
    class Meta:
        model = IndividualRoleInHousehold

    role = ROLE_PRIMARY
