from collections import defaultdict
import logging
from typing import Any
import uuid

import openpyxl

from hope.apps.core.models import BusinessArea
from hope.apps.generic_import.generic_upload_service.parsers.base_parser import BaseParser
from hope.apps.geo.models import Area, Country
from hope.apps.payment.models.payment import FinancialInstitution

logger = logging.getLogger(__name__)


class XlsxSomaliaParser(BaseParser):
    """Parser for Somalia Excel format with household and individual data."""

    REQUIRED_COLUMNS = [
        "HouseholdCSSPID",
        "IndividualID",
        "IndividualName",
        "Sex",
        "IndividualDateOfBirth",
        "District",
        "Village",
        "HouseholdSize",
    ]

    def __init__(self, business_area: BusinessArea | None = None):
        self._business_area = business_area
        self._households = {}
        self._individuals = []
        self._accounts = []
        self._documents = []
        self._identities = []
        self._individual_roles = []
        self._errors = []
        self._file_path = None
        self._parsed = False
        self._admin_areas = dict(Area.objects.values_list("name", "id"))
        # Cache Somalia country ID
        try:
            self._somalia_country_id = Country.objects.get(iso_code3="SOM").id
        except Country.DoesNotExist:
            self._somalia_country_id = None

        # Cache financial institution on initialization to avoid repeated queries
        self._financial_institution = self._get_financial_institution_for_account()

    def _get_financial_institution_for_account(self) -> FinancialInstitution | None:
        """Get Financial Institution based on BusinessArea countries.

        Returns first FI that matches any of the BusinessArea's countries.
        """
        if not self._business_area:
            return None

        # Get countries from BusinessArea
        ba_countries = self._business_area.countries.all()
        if not ba_countries.exists():
            return None

        # Query FinancialInstitution by country
        return FinancialInstitution.objects.filter(country__in=ba_countries).first()

    def parse(self, file_path: str) -> None:
        """Parse the Excel file and extract all data."""
        self._file_path = file_path
        self._errors = []

        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            headers = [cell.value for cell in sheet[1]]

            if not self._validate_headers(headers):
                return
            households_raw = defaultdict(list)
            for _row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):
                    continue
                row_data = dict(zip(headers, row, strict=False))
                household_id = row_data.get("HouseholdCSSPID")
                if household_id:
                    households_raw[household_id].append(row_data)
            for household_id, rows in households_raw.items():
                self._process_household(household_id, rows)

            self._parsed = True

        except Exception as e:
            logger.exception(f"Error parsing file {file_path}: {e}")
            self._errors.append(f"Error parsing file: {str(e)}")

    def _validate_headers(self, headers: list[str]) -> bool:
        """Validate that all required columns are present."""
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in headers]
        if missing_columns:
            self._errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        return True

    def _process_household(self, household_id: str, rows: list[dict]) -> None:
        if not rows:
            return
        first_row = rows[0]
        household_data = {
            "id": uuid.uuid4().hex,
            "size": self._parse_int(first_row.get("HouseholdSize", 0)),
            "village": first_row.get("Village") or "",
            "address": first_row.get("District") or "",
            "admin1": self._admin_areas.get(first_row.get("District") or ""),  # District as admin level 1
            "country": self._somalia_country_id,
            "pregnant_count": self._parse_int(first_row.get("PregnantCount", 0)),
            "flex_fields": {
                "lactating_count_h_f": self._parse_int(first_row.get("LactatingCount", 0)),
                "infant_count_h_f": self._parse_int(first_row.get("InfantCount", 0)),
                "entitlement_amount_h_f": self._parse_float(first_row.get("EntitlementAmount", 0)),
                "mpsp_h_f": first_row.get("MPSP") or "",
                "household_cssp_id_h_f": household_id,
            },
        }

        # Process first individual as head of household
        head_of_household = self._process_individual(first_row, household_data["id"])
        household_data["head_of_household_id"] = head_of_household["id"]

        # Add household to collection with head_of_household_id already set
        self._households[household_id] = household_data

        # Process remaining individuals
        for _idx, row in enumerate(rows[1:]):
            self._process_individual(row, household_data["id"])

    def _process_individual(self, row: dict, household_id: str) -> dict[str, Any]:
        custom_individual_id = row.get("IndividualID")
        individual_id = uuid.uuid4().hex
        full_name = row.get("IndividualName") or ""
        name_parts = full_name.split() if full_name else []
        given_name = name_parts[0] if name_parts else ""
        family_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        sex = (row.get("Sex") or "").lower()
        if sex in ["female", "f"]:
            sex = "FEMALE"
        elif sex in ["male", "m"]:
            sex = "MALE"
        else:
            sex = "MALE"  # Default
        dob = row.get("IndividualDateOfBirth")
        if isinstance(dob, str):
            pass
        elif dob:
            dob = dob.strftime("%Y-%m-%d") if hasattr(dob, "strftime") else str(dob)

        individual_data = {
            "id": individual_id,
            "household_id": household_id,
            "given_name": given_name,
            "family_name": family_name,
            "full_name": full_name,
            "birth_date": dob,
            "sex": sex,
            "relationship": "HEAD",
            "phone_no": self._format_phone(row.get("IndividualPhoneNumber")),
            "flex_fields": {"individual_id_i_f": custom_individual_id},
        }

        self._individuals.append(individual_data)
        self._process_documents(row, individual_id)
        wallet_phone = row.get("WalletPhoneNumber")
        if wallet_phone:
            # Use cached financial institution instead of querying every time
            account_data = {
                "individual_id": individual_id,
                "account_type": "mobile",
                "number": self._format_phone(wallet_phone),
                "financial_institution_id": self._financial_institution.id if self._financial_institution else None,
                "data": {
                    "provider": row.get("MPSP") or "",
                },
            }
            self._accounts.append(account_data)
        return individual_data

    def _process_documents(self, row: dict, individual_id: str):
        doc_type = row.get("IndividualIDDocument")
        doc_number = row.get("IndividualIDNumber")
        if doc_number and doc_number != "None":
            document_data = {
                "individual_id": individual_id,
                "type_key": doc_type.lower() if doc_type and doc_type != "None" else "other_id",
                "document_number": str(doc_number),
                "country": "SOM",
            }
            self._documents.append(document_data)

    def _parse_int(self, value: Any) -> int:
        if value is None or value == "":
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    def _parse_float(self, value: Any) -> float:
        if value is None or value == "":
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _format_phone(self, phone: Any) -> str:
        if not phone:
            return ""
        phone_str = str(phone).strip()
        # Add + prefix if numeric and doesn't already have it
        if phone_str and not phone_str.startswith("+") and phone_str.replace(".", "").isdigit():
            # Remove any decimal point (from Excel float conversion)
            phone_str = phone_str.split(".")[0]
            phone_str = f"+{phone_str}"
        return phone_str

    def validate_file_structure(self) -> bool:
        if not self._parsed:
            return False
        return len(self._errors) == 0

    @property
    def errors(self) -> list[str]:
        return self._errors

    @property
    def supported_file_types(self) -> list[str]:
        return [".xlsx", ".xls"]

    @property
    def households_data(self) -> list[dict[str, Any]]:
        return list(self._households.values())

    @property
    def individuals_data(self) -> list[dict[str, Any]]:
        return self._individuals

    @property
    def individual_roles_in_households_data(self) -> list[dict[str, Any]]:
        return self._individual_roles

    @property
    def accounts_data(self) -> list[dict[str, Any]]:
        """Return list of account dictionaries."""
        return self._accounts

    @property
    def documents_data(self) -> list[dict[str, Any]]:
        """Return list of document dictionaries."""
        return self._documents

    @property
    def identities_data(self) -> list[dict[str, Any]]:
        """Return list of identity dictionaries."""
        return self._identities
