from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.services.xlsx_export_targeting_service import (
    XlsxExportTargetingService,
)


class TestXlsxExportTargetingService(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.target_population = TargetPopulationFactory(
            business_area=cls.business_area, status=TargetPopulation.STATUS_OPEN
        )

    def test_add_version(self) -> None:
        service = XlsxExportTargetingService(self.target_population)
        service._create_workbook()
        service._add_version()
        self.assertEqual(
            service.ws_meta[XlsxExportTargetingService.VERSION_CELL_NAME_COORDINATES].value,
            XlsxExportTargetingService.VERSION_CELL_NAME,
        )
        self.assertEqual(
            service.ws_meta[XlsxExportTargetingService.VERSION_CELL_COORDINATES].value,
            XlsxExportTargetingService.VERSION,
        )

    def test_add_standard_columns_headers(self) -> None:
        service = XlsxExportTargetingService(self.target_population)
        service._create_workbook()
        service._add_standard_columns_headers()
        headers = [cell.value for cell in service.ws_individuals[1]]
        self.assertEqual(headers, ["Household unicef_id", "unicef_id", "Linked Households", "Bank account information"])
