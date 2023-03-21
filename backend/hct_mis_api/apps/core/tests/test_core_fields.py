from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
    CORE_FIELDS_ATTRIBUTES,
)


class TestCoreFields(APITestCase):
    def test_all_fields_have_lookup(self) -> None:
        for field in CORE_FIELDS_ATTRIBUTES:
            self.assertTrue(field.get("lookup"), f'{field.get("name")} does not have a lookup')
