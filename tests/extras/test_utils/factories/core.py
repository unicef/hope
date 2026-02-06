"""Core-related factories."""

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
import factory
from factory.django import DjangoModelFactory

from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    CountryCodeMap,
    DataCollectingType,
    FileTemp,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    PeriodicFieldData,
    StorageFile,
    XLSXKoboTemplate,
)


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


class CountryCodeMapFactory(DjangoModelFactory):
    class Meta:
        model = CountryCodeMap
        django_get_or_create = ("ca_code",)

    ca_code = factory.Sequence(lambda n: f"C{n:02d}")
    country = factory.SubFactory("extras.test_utils.factories.geo.CountryFactory")


class DataCollectingTypeFactory(DjangoModelFactory):
    class Meta:
        model = DataCollectingType

    code = factory.Sequence(lambda n: f"dct_{n}")
    label = factory.Sequence(lambda n: f"DCT {n}")
    type = DataCollectingType.Type.STANDARD


class PeriodicFieldDataFactory(DjangoModelFactory):
    class Meta:
        model = PeriodicFieldData

    subtype = PeriodicFieldData.STRING
    number_of_rounds = 1
    rounds_names = factory.LazyAttribute(lambda o: [f"Round {i + 1}" for i in range(o.number_of_rounds)])


class FlexibleAttributeFactory(DjangoModelFactory):
    class Meta:
        model = FlexibleAttribute

    name = factory.Sequence(lambda n: f"flex_attr_{n}")
    type = FlexibleAttribute.STRING
    associated_with = FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
    label = factory.LazyFunction(lambda: {"English(EN)": "Flex Field"})


class FlexibleAttributeChoiceFactory(DjangoModelFactory):
    class Meta:
        model = FlexibleAttributeChoice

    name = factory.Sequence(lambda n: f"choice_{n}")
    list_name = factory.Sequence(lambda n: f"List {n}")
    label = factory.LazyFunction(lambda: {"English(EN)": "Choice"})


class XLSXKoboTemplateFactory(DjangoModelFactory):
    class Meta:
        model = XLSXKoboTemplate

    file_name = factory.Sequence(lambda n: f"template_{n}.xlsx")
    status = XLSXKoboTemplate.UPLOADED
    file = factory.LazyAttribute(lambda o: ContentFile(b"test content", name=o.file_name))


class FileTempFactory(DjangoModelFactory):
    class Meta:
        model = FileTemp

    file = factory.LazyFunction(lambda: SimpleUploadedFile("test.txt", b"test"))


class StorageFileFactory(DjangoModelFactory):
    class Meta:
        model = StorageFile

    business_area = factory.SubFactory(BusinessAreaFactory)
    file = factory.LazyFunction(lambda: SimpleUploadedFile("storage.txt", b"test"))
