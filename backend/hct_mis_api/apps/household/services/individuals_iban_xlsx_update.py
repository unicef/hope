import logging

import openpyxl

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.household.models import Individual, XlsxUpdateFile, BankAccountInfo


logger = logging.getLogger(__name__)


class IndividualsIBANXlsxUpdateException(Exception):
    pass


class IndividualsIBANXlsxUpdate:
    DATA_ROW_INDEX = 2
    STATUS_UNIQUE = "UNIQUE"
    STATUS_NO_MATCH = "NO_MATCH"
    STATUS_MULTIPLE_MATCH = "MULTIPLE_MATCH"

    MATCHING_COLUMN = "UNICEF_ID"
    UPDATE_COLUMNS = ["IBAN", "BANK_NAME"]
    SPREADSHEET_NAME = "Individuals"

    def __init__(self, xlsx_update_file: XlsxUpdateFile):
        self.validation_errors = []
        self.report_dict = {}

        self.xlsx_update_file = xlsx_update_file
        self.business_area = self.xlsx_update_file.business_area
        self.wb = openpyxl.load_workbook(xlsx_update_file.file, data_only=True)
        self.individuals_ws = self.wb[self.SPREADSHEET_NAME]

    def _build_helpers(self):
        first_row = self.individuals_ws[1]
        self.columns_names_index_dict = {cell.value: cell.col_idx for cell in first_row}
        self.matching_column_index = self.columns_names_index_dict[self.MATCHING_COLUMN]
        self.iban_update_column_index = self.columns_names_index_dict[self.UPDATE_COLUMNS[0]]
        self.bank_name_update_column_index = self.columns_names_index_dict[self.UPDATE_COLUMNS[1]]

    def _row_report_data(self, row):
        return row[0].row

    def _get_queryset(self):
        return Individual.objects.filter(business_area=self.business_area, duplicate=False, withdrawn=False)

    def validate(self):
        self._validate_columns_names()
        if self.validation_errors:
            return

        self._build_helpers()
        self._create_matching_report()
        self._validate_matching_report()

    def _validate_columns_names(self):
        first_row = self.individuals_ws[1]

        columns = [cell.value for cell in first_row]

        if self.MATCHING_COLUMN not in columns:
            self.validation_errors.append(f"No {self.MATCHING_COLUMN} column in provided file")
        for column in self.UPDATE_COLUMNS:
            if column not in columns:
                self.validation_errors.append(f"No {column} column in provided file")

    def _get_matching_report_for_single_row(self, row):
        filter_value = row[self.matching_column_index - 1].value
        individuals = self._get_queryset().filter(**{self.MATCHING_COLUMN.lower(): filter_value})
        if not individuals.count():
            return self.STATUS_NO_MATCH, self._row_report_data(row)
        elif individuals.count() > 1:
            return self.STATUS_MULTIPLE_MATCH, self._row_report_data(row)
        return self.STATUS_UNIQUE, (self._row_report_data(row), individuals.first())

    def _create_matching_report(self):
        report_dict = {
            self.STATUS_UNIQUE: [],
            self.STATUS_NO_MATCH: [],
            self.STATUS_MULTIPLE_MATCH: [],
        }
        for row in self.individuals_ws.iter_rows(min_row=self.DATA_ROW_INDEX):
            (status, data) = self._get_matching_report_for_single_row(row)
            report_dict[status].append(data)

        self.report_dict = report_dict

    def _validate_matching_report(self):
        if no_match := self.report_dict[self.STATUS_NO_MATCH]:
            self.validation_errors.append(f"No matching Individuals for rows: {no_match}")

        if multiple_match := self.report_dict[self.STATUS_MULTIPLE_MATCH]:
            self.validation_errors.append(f"Multiple matching Individuals for rows: {multiple_match}")

    @transaction.atomic
    def update(self):
        for individuals_unique_report in self.report_dict[self.STATUS_UNIQUE]:
            row_num, individual = individuals_unique_report
            row = self.individuals_ws[row_num]

            new_iban = row[self.iban_update_column_index - 1].value
            new_bank_name = row[self.bank_name_update_column_index - 1].value

            if not new_iban or not new_bank_name:
                raise IndividualsIBANXlsxUpdateException(
                    f"BankAccountInfo data is missing for Individual {individual.unicef_id} in Row {row_num},"
                    f" One of IBAN/BANK_NAME value was not provided."
                    f" Please validate also other rows for missing data."
                )

            if not individual.bank_account_info.exists():
                BankAccountInfo.objects.create(
                    individual=individual, bank_name=new_bank_name, bank_account_number=new_iban
                )

            else:
                updated_bank_accounts = []
                for bank_account_info in individual.bank_account_info.all():
                    bank_account_info.bank_account_number = new_iban
                    bank_account_info.bank_name = new_bank_name
                    updated_bank_accounts.append(bank_account_info)

                BankAccountInfo.objects.bulk_update(updated_bank_accounts, ["bank_account_number", "bank_name"])

    def _get_email_context(self, message: str):
        return {
            "first_name": self.xlsx_update_file.uploaded_by.first_name,
            "last_name": self.xlsx_update_file.uploaded_by.last_name,
            "email": self.xlsx_update_file.uploaded_by.email,
            "message": message,
            "upload_file_id": str(self.xlsx_update_file.id),
        }

    def send_failure_email(self):
        email = self._prepare_email(context=self._get_email_context(message=str(self.validation_errors)))
        try:
            email.send()
        except Exception as e:
            logger.exception(e)

    def send_success_email(self):
        email = self._prepare_email(
            context=self._get_email_context(message="All of the Individuals IBAN number we're updated successfully")
        )
        try:
            email.send()
        except Exception as e:
            logger.exception(e)

    @classmethod
    def send_error_email(cls, error_message: str, xlsx_update_file_id: str, uploaded_by: User):
        message = f"There was an unexpected error during Individuals IBAN update: {error_message}"
        context = {
            "first_name": uploaded_by.first_name,
            "last_name": uploaded_by.last_name,
            "email": uploaded_by.email,
            "message": message,
            "upload_file_id": xlsx_update_file_id,
        }
        email = cls._prepare_email(context=context)
        try:
            email.send()
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def _prepare_email(context: dict):
        text_body = render_to_string(
            "admin/household/individual/individuals_iban_xlsx_update_email.txt", context=context
        )
        html_body = render_to_string(
            "admin/household/individual/individuals_iban_xlsx_update_email.txt", context=context
        )

        email = EmailMultiAlternatives(
            subject=f"Individual IBANs xlsx [{context['upload_file_id']}] update result",
            from_email=settings.EMAIL_HOST_USER,
            to=[context["email"]],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")

        return email
