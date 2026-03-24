"""Registration data related factories."""

from decimal import Decimal
from typing import Any

import factory
from factory.django import DjangoModelFactory

from hope.models import DeduplicationEngineSimilarityPair, ImportData, KoboImportData, RegistrationDataImport

from .account import UserFactory
from .core import BusinessAreaFactory
from .program import ProgramFactory


class ImportDataFactory(DjangoModelFactory):
    class Meta:
        model = ImportData

    status = ImportData.STATUS_PENDING
    data_type = ImportData.XLSX
    business_area_slug = ""
    file = factory.django.FileField(filename="test_data.xlsx")


class KoboImportDataFactory(DjangoModelFactory):
    class Meta:
        model = KoboImportData

    status = ImportData.STATUS_FINISHED
    data_type = ImportData.JSON
    business_area_slug = "afghanistan"
    kobo_asset_id = factory.Sequence(lambda n: f"kobo_asset_{n}")
    only_active_submissions = True
    pull_pictures = True


class RegistrationDataImportFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport

    name = factory.Sequence(lambda n: f"RDI {n}")
    data_source = RegistrationDataImport.XLS
    status = RegistrationDataImport.MERGED
    number_of_individuals = 1
    number_of_households = 1
    imported_by = factory.SubFactory(UserFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)
    program = factory.SubFactory(ProgramFactory, business_area=factory.SelfAttribute("..business_area"))


class DeduplicationEngineSimilarityPairFactory(DjangoModelFactory):
    class Meta:
        model = DeduplicationEngineSimilarityPair

    program = factory.SubFactory(ProgramFactory)
    individual1 = factory.SubFactory(
        "extras.test_utils.factories.household.IndividualFactory",
        program=factory.SelfAttribute("..program"),
    )
    individual2 = factory.SubFactory(
        "extras.test_utils.factories.household.IndividualFactory",
        program=factory.SelfAttribute("..program"),
    )
    similarity_score = Decimal("55.55")
    status_code = DeduplicationEngineSimilarityPair.StatusCode.STATUS_200

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> DeduplicationEngineSimilarityPair:
        individual1 = kwargs.get("individual1")
        individual2 = kwargs.get("individual2")
        if individual1 and individual2 and individual1.id > individual2.id:
            kwargs["individual1"], kwargs["individual2"] = individual2, individual1

        return super()._create(model_class, *args, **kwargs)
