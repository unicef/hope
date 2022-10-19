from faker import Faker

from hct_mis_api.apps.core.models import BusinessArea

faker = Faker()


def create_afghanistan() -> BusinessArea:
    return BusinessArea.objects.create(
        **{
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
        },
    )
