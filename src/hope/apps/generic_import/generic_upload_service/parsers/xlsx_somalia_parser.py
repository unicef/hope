from collections import defaultdict
import logging
from typing import Any
import uuid

import openpyxl

from hope.apps.generic_import.generic_upload_service.parsers.base_parser import BaseParser

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

    def __init__(self):
        self._households = {}
        self._individuals = []
        self._accounts = []
        self._documents = []
        self._identities = []
        self._individual_roles = []
        self._errors = []
        self._file_path = None
        self._parsed = False

    def parse(self, file_path: str) -> None:
        """Parse the Excel file and extract all data."""
        self._file_path = file_path
        self._errors = []

        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            headers = []
            for cell in sheet[1]:
                headers.append(cell.value)

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
            "village": first_row.get("Village", ""),
            "address": first_row.get("District", ""),
            "admin1": first_row.get("District", ""),  # District as admin level 1
            "country": "SOM",
            "pregnant_count": self._parse_int(first_row.get("PregnantCount", 0)),
            "flex_fields": {
                "lactating_count_h_f": self._parse_int(first_row.get("LactatingCount", 0)),
                "infant_count_h_f": self._parse_int(first_row.get("InfantCount", 0)),
                "entitlement_amount_h_f": self._parse_float(first_row.get("EntitlementAmount", 0)),
                "mpsp_h_f": first_row.get("MPSP", ""),
                "household_cssp_id_h_f": household_id,
            },
        }

        self._households[household_id] = household_data
        for _idx, row in enumerate(rows):
            self._process_individual(row, household_data["id"])

    def _process_individual(self, row: dict, household_id: str) -> None:
        custom_individual_id = row.get("IndividualID")
        individual_id = uuid.uuid4().hex
        full_name = row.get("IndividualName", "")
        name_parts = full_name.split()
        given_name = name_parts[0] if name_parts else ""
        family_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        sex = row.get("Sex", "").lower()
        if sex in ["female", "f"]:
            sex = "FEMALE"
        elif sex in ["male", "m"]:
            sex = "MALE"
        else:
            sex = "MALE"  # Default
        dob = row.get("IndividualDateOfBirth")
        if isinstance(dob, str):
            dob = dob
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
            account_data = {
                "individual_id": individual_id,
                "account_type": "mobile_money",
                "number": self._format_phone(wallet_phone),
                "data": {
                    "provider": row.get("MPSP", ""),
                },
            }
            self._accounts.append(account_data)

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
        return str(phone).strip()

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
    def households_data(self) -> list[dict]:
        return list(self._households.values())

    @property
    def individuals_data(self) -> list[dict]:
        return self._individuals

    @property
    def individual_roles_in_households_data(self) -> list[dict]:
        return self._individual_roles

    @property
    def accounts_data(self) -> list[dict]:
        """Return list of account dictionaries."""
        return self._accounts

    @property
    def documents_data(self) -> list[dict]:
        """Return list of document dictionaries."""
        return self._documents

    @property
    def identities_data(self) -> list[dict]:
        """Return list of identity dictionaries."""
        return self._identities
