"""Core-related factories."""

from typing import Any

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
import factory
from factory.django import DjangoModelFactory

from hope.apps.periodic_data_update.utils import field_label_to_field_name
from hope.models import (
    AsyncJob,
    BeneficiaryGroup,
    BusinessArea,
    CountryCodeMap,
    DataCollectingType,
    Facility,
    FileTemp,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    PaymentPlanPurpose,
    PeriodicFieldData,
    StorageFile,
    UniversalUpdate,
    XLSXKoboTemplate,
)
from hope.models.async_job import PeriodicAsyncJob
from hope.models.currency import Currency


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


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency
        django_get_or_create = ("code",)

    code = "PLN"
    name = "Polish Zloty"


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


class FlexibleAttributeForPDUFactory(DjangoModelFactory):
    class Meta:
        model = FlexibleAttribute

    type = FlexibleAttribute.PDU
    associated_with = FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
    label = factory.Sequence(lambda n: f"pdu_attr_{n}")
    name = factory.LazyAttribute(lambda instance: field_label_to_field_name(instance.label))
    pdu_data = factory.SubFactory(PeriodicFieldDataFactory)
    program = factory.SubFactory("extras.test_utils.factories.program.ProgramFactory")

    @classmethod
    def _create(cls, target_class: Any, *args: Any, **kwargs: Any) -> FlexibleAttribute:
        label = kwargs.pop("label", None)
        kwargs["label"] = {"English(EN)": label}
        return super()._create(target_class, *args, **kwargs)


class FlexibleAttributeChoiceFactory(DjangoModelFactory):
    class Meta:
        model = FlexibleAttributeChoice

    name = factory.Sequence(lambda n: f"choice_{n}")
    list_name = factory.Sequence(lambda n: f"List {n}")
    label = factory.LazyFunction(lambda: {"English(EN)": "Choice"})


class FlexibleAttributeGroupFactory(DjangoModelFactory):
    class Meta:
        model = FlexibleAttributeGroup

    name = factory.Sequence(lambda n: f"flex_group_{n}")
    label = factory.LazyFunction(lambda: {"English(EN)": "Group"})


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


class FacilityFactory(DjangoModelFactory):
    class Meta:
        model = Facility
        django_get_or_create = ("name", "business_area")

    business_area = factory.SubFactory(BusinessAreaFactory)
    admin_area = factory.SubFactory("extras.test_utils.factories.geo.AreaFactory")
    name = factory.Sequence(lambda n: f"Facility {n}")


class AsyncJobFactory(DjangoModelFactory):
    class Meta:
        model = AsyncJob

    job_name = factory.Sequence(lambda n: f"job_{n}")


class PeriodicAsyncJobFactory(DjangoModelFactory):
    class Meta:
        model = PeriodicAsyncJob

    job_name = factory.Sequence(lambda n: f"periodic_job_{n}")


class UniversalUpdateFactory(DjangoModelFactory):
    class Meta:
        model = UniversalUpdate

    program = factory.SubFactory("extras.test_utils.factories.program.ProgramFactory")


class PaymentPlanPurposeFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlanPurpose

    business_area = factory.SubFactory(BusinessAreaFactory)
    name = factory.Sequence(lambda n: f"Purpose {n}")
