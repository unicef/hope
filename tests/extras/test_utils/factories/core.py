import random
from typing import Any, List

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
    StorageFile,
)
from hct_mis_api.apps.periodic_data_update.utils import field_label_to_field_name
from hct_mis_api.apps.program.models import Program

faker = Faker()


def create_afghanistan() -> BusinessArea:
    return BusinessArea.objects.get_or_create(
        code="0060",
        defaults={
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "kobo_token": "XXX",
        },
    )[0]


def create_ukraine() -> BusinessArea:
    return BusinessArea.objects.create(
        **{
            "code": "4410",
            "name": "Ukraine",
            "long_name": "UKRAINE",
            "region_code": "66",
            "region_name": "ECAR",
            "slug": "ukraine",
            "has_data_sharing_agreement": True,
            "kobo_token": "YYY",
        }
    )


def create_kenya() -> BusinessArea:
    return BusinessArea.objects.create(
        **{
            "code": "2400",
            "name": "Kenya",
            "long_name": "THE REPUBLIC OF KENYA",
            "region_code": "63",
            "region_name": "ESAR",
            "slug": "kenya",
            "has_data_sharing_agreement": True,
            "kobo_token": "ZZZ",
        }
    )


class StorageFileFactory(DjangoModelFactory):
    class Meta:
        model = StorageFile

    business_area = factory.LazyAttribute(lambda _: BusinessArea.objects.first())


def generate_data_collecting_types() -> None:
    data_collecting_types = [
        {"label": "Partial", "code": "partial_individuals", "description": "Partial individuals collected"},
        {"label": "Full", "code": "full_collection", "description": "Full individual collected"},
        {"label": "Size only", "code": "size_only", "description": "Size only collected"},
        {
            "label": "size/age/gender disaggregated",
            "code": "size_age_gender_disaggregated",
            "description": "No individual data",
        },
    ]

    for data_dict in data_collecting_types:
        DataCollectingType.objects.update_or_create(**data_dict)


class DataCollectingTypeFactory(DjangoModelFactory):
    class Meta:
        model = DataCollectingType
        django_get_or_create = ("label", "code")

    label = factory.Faker("text", max_nb_chars=30)
    code = factory.Faker("text", max_nb_chars=30)
    type = DataCollectingType.Type.STANDARD
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    individual_filters_available = True
    household_filters_available = True

    @factory.post_generation
    def business_areas(self, create: Any, extracted: List[Any], **kwargs: Any) -> None:
        if not create:
            return

        if extracted:
            for business_area in extracted:
                self.limit_to.add(business_area)


class PeriodicFieldDataFactory(DjangoModelFactory):
    subtype = fuzzy.FuzzyChoice([choice[0] for choice in PeriodicFieldData.TYPE_CHOICES])
    rounds_names = factory.LazyAttribute(
        lambda _: [factory.Faker("word").evaluate(None, None, {"locale": None}) for _ in range(random.randint(1, 10))]
    )
    number_of_rounds = factory.LazyAttribute(lambda o: len(o.rounds_names))

    class Meta:
        model = PeriodicFieldData


class FlexibleAttributeForPDUFactory(DjangoModelFactory):
    associated_with = FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
    label = factory.Faker("word")
    name = factory.LazyAttribute(lambda instance: field_label_to_field_name(instance.label))
    type = FlexibleAttribute.PDU
    pdu_data = factory.SubFactory(PeriodicFieldDataFactory)

    @factory.lazy_attribute
    def program(self) -> Any:
        from tests.extras.test_utils.factories.fixtures import ProgramFactory

        return ProgramFactory()

    @classmethod
    def _create(cls, target_class: Any, *args: Any, **kwargs: Any) -> FlexibleAttribute:
        label = kwargs.pop("label", None)
        kwargs["label"] = {"English(EN)": label}
        obj = super()._create(target_class, *args, **kwargs)
        return obj

    class Meta:
        model = FlexibleAttribute


def create_pdu_flexible_attribute(
    label: str, subtype: str, number_of_rounds: int, rounds_names: list[str], program: Program
) -> FlexibleAttribute:
    name = field_label_to_field_name(label)
    flexible_attribute = FlexibleAttribute.objects.create(
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": label},
        name=name,
        program=program,
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=number_of_rounds, rounds_names=rounds_names
    )
    flexible_attribute.save()
    return flexible_attribute
