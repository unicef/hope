"""Registration data related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import RegistrationDataImport

from .account import UserFactory


class RegistrationDataImportFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport

    name = factory.Sequence(lambda n: f"RDI {n}")
    data_source = RegistrationDataImport.XLS
    status = RegistrationDataImport.MERGED
    number_of_individuals = 1
    number_of_households = 1
    imported_by = factory.SubFactory(UserFactory)
