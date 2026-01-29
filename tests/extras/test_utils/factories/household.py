"""Household-related factories."""

from datetime import date

from django.utils import timezone
import factory
from factory.django import DjangoModelFactory

from hope.apps.household.const import ROLE_PRIMARY
from hope.models import (
    Document,
    DocumentType,
    EntitlementCard,
    Household,
    Individual,
    IndividualRoleInHousehold,
    MergeStatusModel,
    RegistrationDataImport,
)

from .core import BusinessAreaFactory
from .program import ProgramFactory
from .registration_data import RegistrationDataImportFactory


class IndividualFactory(DjangoModelFactory):
    class Meta:
        model = Individual

    full_name = factory.Sequence(lambda n: f"Person {n}")
    sex = "MALE"
    birth_date = date(1990, 1, 1)
    first_registration_date = factory.LazyFunction(date.today)
    last_registration_date = factory.LazyFunction(date.today)
    rdi_merge_status = MergeStatusModel.MERGED
    business_area = factory.SubFactory(BusinessAreaFactory)
    program = factory.SubFactory(ProgramFactory, business_area=factory.SelfAttribute("..business_area"))
    registration_data_import = factory.SubFactory(
        RegistrationDataImportFactory,
        business_area=factory.SelfAttribute("..business_area"),
        program=factory.SelfAttribute("..program"),
    )


class HouseholdFactory(DjangoModelFactory):
    class Meta:
        model = Household

    first_registration_date = factory.LazyFunction(timezone.now)
    last_registration_date = factory.LazyFunction(timezone.now)
    rdi_merge_status = MergeStatusModel.MERGED
    business_area = factory.SubFactory(BusinessAreaFactory)
    program = factory.SubFactory(ProgramFactory, business_area=factory.SelfAttribute("..business_area"))

    @factory.post_generation
    def head_of_household(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.head_of_household = extracted
            individual = extracted
            if individual.household_id != self.pk:
                individual.household = self
                individual.save(update_fields=["household"])
            self.save()
            return

        from .registration_data import RegistrationDataImportFactory

        rdi = self.registration_data_import
        if rdi is None:
            rdi = RegistrationDataImportFactory(
                business_area=self.business_area,
                program=self.program,
                status=RegistrationDataImport.MERGED
                if self.rdi_merge_status == MergeStatusModel.MERGED
                else RegistrationDataImport.IN_REVIEW,
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

    @factory.post_generation
    def create_role(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted is False:
            return
        if not self.head_of_household:
            return
        IndividualRoleInHouseholdFactory(
            household=self,
            individual=self.head_of_household,
            rdi_merge_status=self.rdi_merge_status,
        )


class IndividualRoleInHouseholdFactory(DjangoModelFactory):
    class Meta:
        model = IndividualRoleInHousehold

    role = ROLE_PRIMARY
    household = factory.SubFactory(HouseholdFactory, create_role=False)
    individual = factory.SubFactory(
        IndividualFactory,
        household=factory.SelfAttribute("..household"),
        business_area=factory.SelfAttribute("..household.business_area"),
        program=factory.SelfAttribute("..household.program"),
        registration_data_import=factory.SelfAttribute("..household.registration_data_import"),
    )


class EntitlementCardFactory(DjangoModelFactory):
    class Meta:
        model = EntitlementCard

    card_number = factory.Sequence(lambda n: f"CARD-{n}")
    card_type = "TYPE"
    current_card_size = "SIZE"
    card_custodian = "CUSTODIAN"
    service_provider = "PROVIDER"
    household = factory.SubFactory(HouseholdFactory)


class DocumentTypeFactory(DjangoModelFactory):
    class Meta:
        model = DocumentType

    label = factory.Sequence(lambda n: f"Document Type {n}")
    key = factory.Sequence(lambda n: f"doc_type_{n}")


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    individual = factory.SubFactory(IndividualFactory)
    program = factory.SelfAttribute("individual.program")
    document_number = factory.Sequence(lambda n: f"DOC-{n}")
    type = factory.SubFactory(DocumentTypeFactory)
