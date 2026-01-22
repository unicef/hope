"""Core-related factories."""

from django.core.files.uploadedfile import SimpleUploadedFile
import factory
from factory.django import DjangoModelFactory

from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, FileTemp


class BusinessAreaFactory(DjangoModelFactory):
    class Meta:
        model = BusinessArea

    code = factory.Sequence(lambda n: f"BA{n:04d}")
    slug = factory.Sequence(lambda n: f"business-area-{n}")
    name = factory.Sequence(lambda n: f"Business Area {n}")
    long_name = factory.Sequence(lambda n: f"Business Area {n} Long Name")
    region_code = "64"
    region_name = "TEST"
    active = True


class BeneficiaryGroupFactory(DjangoModelFactory):
    class Meta:
        model = BeneficiaryGroup

    name = factory.Sequence(lambda n: f"Group {n}")
    group_label = "Household"
    group_label_plural = "Households"
    member_label = "Individual"
    member_label_plural = "Individuals"


class DataCollectingTypeFactory(DjangoModelFactory):
    class Meta:
        model = DataCollectingType

    code = factory.Sequence(lambda n: f"dct_{n}")
    label = factory.Sequence(lambda n: f"DCT {n}")


class FileTempFactory(DjangoModelFactory):
    class Meta:
        model = FileTemp

    file = factory.LazyFunction(lambda: SimpleUploadedFile("test.txt", b"test"))
