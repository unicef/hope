from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db import transaction
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


class ExportUsersXlsx:
    FIELDS_TO_COLUMNS_MAPPING = OrderedDict(
        {
            "first_name": "FIRST NAME",
            "last_name": "LAST NAME",
            "email": "E-MAIL",
            "status": "ACCOUNT STATUS",
            "partner": "PARTNER",
            "user_roles": "USER ROLES",
        }
    )

    def __init__(self, business_area_slug):
        self.business_area_slug = business_area_slug
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = "Exported Users to Cash Assist"
        self._add_headers()

    def _add_headers(self):
        self.ws.append(list(self.FIELDS_TO_COLUMNS_MAPPING.values()))
        for i in range(1, len(self.FIELDS_TO_COLUMNS_MAPPING) + 1):
            self.ws.column_dimensions[get_column_letter(i)].width = 20

    @transaction.atomic(using="default")
    def get_exported_users_file(self):
        user_fields = self.FIELDS_TO_COLUMNS_MAPPING.keys()
        users = get_user_model().objects.prefetch_related("user_roles").filter(
            available_for_export=True, is_superuser=False, user_roles__business_area__slug=self.business_area_slug
        )
        if users.exists() is False:
            return

        for user in users:
            row = [getattr(user, field) for field in user_fields if field != "user_roles"]
            all_roles = user.user_roles.filter(business_area__slug=self.business_area_slug)
            row.append(", ".join([f"{role.business_area.name}-{role.role.name}" for role in all_roles]))
            self.ws.append(row)

        users.update(available_for_export=False)

        return self.wb
