from faker import Faker

faker = Faker()


def create_afghanistan():
    from hct_mis_api.apps.core.models import BusinessArea

    BusinessArea.objects.create(
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
