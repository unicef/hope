import json
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List

from django.core.files import File

from hct_mis_api.apps.dashboard.models import DashReport
from hct_mis_api.apps.dashboard.serializers import DashboardHouseholdSerializer
from hct_mis_api.apps.household.models import Household


class GenerateDashReportService:
    """
    Service class responsible for generating DashReports for a specific business area.

    Attributes:
        report (DashReport): The DashReport instance being generated.
        business_area (BusinessArea): The business area associated with the report.
    """

    def __init__(self, report: DashReport) -> None:
        """
        Initializes the GenerateDashReportService with the given DashReport.

        Args:
            report (DashReport): The DashReport instance to be processed.
        """
        self.report = report
        self.business_area = report.business_area

    def _serialize_data(self) -> List[Dict[str, Any]]:
        """
        Serializes the household data for the given business area into a list of dictionaries.

        Uses the DashboardHouseholdSerializer to serialize household data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing serialized household data.
        """
        households = Household.objects.using("read_only").filter(business_area=self.business_area)
        serialized_data = DashboardHouseholdSerializer(households, many=True).data
        return list(serialized_data)

    def _save_report_file(self, data: List[Dict[str, Any]]) -> None:
        """
        Saves the serialized data to a JSON file and attaches it to the report.

        The data is first written to a temporary file, which is then saved as a File object
        and linked to the DashReport.

        Args:
            data (List[Dict[str, Any]]): The serialized household data to be saved.
        """
        with NamedTemporaryFile(suffix=".json", mode="w+") as tmp_file:
            json.dump(data, tmp_file, indent=4)
            tmp_file.flush()
            tmp_file.seek(0)
            self.report.file.save(f"{self.business_area.slug}_report.json", File(tmp_file), save=False)

    def generate_report(self) -> None:
        """
        Generates the DashReport by serializing the household data and saving it to a file.

        This method sets the report status to 'COMPLETED' if successful, and 'FAILED' if an exception occurs.
        """
        try:
            data = self._serialize_data()
            self._save_report_file(data)
            self.report.status = DashReport.COMPLETED
        except Exception as e:
            self.report.status = DashReport.FAILED
            print(f"Error: {e}")
        finally:
            self.report.save()
