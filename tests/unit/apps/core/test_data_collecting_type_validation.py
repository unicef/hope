from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import DataCollectingType


class TestDCTValidation(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = BusinessAreaFactory()

    def test_change_type_without_compatible_with_different_type(self) -> None:
        dct_full = DataCollectingTypeFactory(label="Full", code="full", business_areas=[self.business_area])

        dct_full.compatible_types.add(dct_full)

        dct_full.type = DataCollectingType.Type.SOCIAL
        dct_full.save()

    def test_change_type_with_compatible_with_different_type(self) -> None:
        dct_full = DataCollectingTypeFactory(label="Full", code="full", business_areas=[self.business_area])
        dct_partial = DataCollectingTypeFactory(label="Partial", code="partial", business_areas=[self.business_area])

        dct_full.compatible_types.add(dct_full)
        dct_full.compatible_types.add(dct_partial)

        dct_full.type = DataCollectingType.Type.SOCIAL

        with self.assertRaises(ValidationError) as error:
            dct_full.save()
        self.assertEqual(
            str(error.exception.messages[0]),
            "Type of DCT cannot be changed if it has compatible DCTs of different type.",
        )

    def test_add_compatible_type_with_different_type(self) -> None:
        dct_full = DataCollectingTypeFactory(label="Full", code="full", business_areas=[self.business_area])
        dct_social = DataCollectingTypeFactory(
            label="SocialDCT",
            code="socialdct",
            business_areas=[self.business_area],
            type=DataCollectingType.Type.SOCIAL,
        )

        dct_full.compatible_types.add(dct_full)

        with self.assertRaises(ValidationError) as error:
            dct_full.compatible_types.add(dct_social)
        self.assertEqual(
            str(error.exception.messages[0]), "DCTs of different types cannot be compatible with each other."
        )
