import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType, StorageFile

faker = Faker()


def create_afghanistan(
    is_payment_plan_applicable: bool = False,
) -> BusinessArea:
    return BusinessArea.objects.create(
        **{
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "is_payment_plan_applicable": is_payment_plan_applicable,
            "kobo_token": "XXX",
        },
    )


class StorageFileFactory(DjangoModelFactory):
    class Meta:
        model = StorageFile

    business_area = factory.LazyAttribute(lambda _: BusinessArea.objects.first())


def generate_data_collecting_types() -> None:
    data_collecting_types = [
        {"code": "0", "description": "Partial individuals collected"},
        {"code": "1", "description": "Full individual collected"},
        {"code": "2", "description": "Size only collected"},
        {"code": "3", "description": "No individual data"},
        {"code": "99", "description": "Unknown"},
    ]

    for data_dict in data_collecting_types:
        DataCollectingType.objects.update_or_create(**data_dict)
