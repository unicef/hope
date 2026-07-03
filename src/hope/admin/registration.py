import csv
from typing import Any

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import JSONField
from django.http import HttpRequest, HttpResponse
from jsoneditor.forms import JSONEditor
from smart_admin.decorators import smart_register

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.contrib.aurora import models
from hope.contrib.aurora.services.nigeria_people_registration_service import NigeriaPeopleRegistrationService


@smart_register(models.Registration)
class RegistrationAdmin(AutocompleteForeignKeyMixin, AdminFiltersMixin, ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "project", "rdi_policy")
    readonly_fields = ("name", "project", "slug", "extra", "metadata")
    list_filter = ("rdi_policy", ("project", AutoCompleteFilter))
    search_fields = ("name",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }

    @staticmethod
    def is_nigeria_registration(registration: models.Registration) -> bool:
        return isinstance(registration.rdi_parser, NigeriaPeopleRegistrationService)

    @staticmethod
    def has_ignored_records(registration: models.Registration) -> bool:
        return models.Record.objects.filter(registration=registration.source_id, ignored=True).exists()

    @button(
        label="Export ignored records",
        permission="aurora.view_record",
        visible=lambda btn: (
            btn.original is not None
            and RegistrationAdmin.is_nigeria_registration(btn.original)
            and RegistrationAdmin.has_ignored_records(btn.original)
        ),
    )
    def export_ignored_records(self, request: HttpRequest, pk: Any) -> HttpResponse:
        registration = models.Registration.objects.get(pk=pk)
        if not self.is_nigeria_registration(registration):
            raise PermissionDenied("Ignored record export is only available for Nigeria Aurora registrations")

        records = models.Record.objects.filter(registration=registration.source_id, ignored=True).order_by("id")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="ignored_aurora_records_{registration.source_id}.csv"'
        fieldnames = [
            "record_id",
            "source_id",
            "registration",
            "timestamp",
            "ignored_reason",
            "account_number",
            "national_id",
            "given_name",
            "middle_name",
            "family_name",
            "phone_number",
        ]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        mapping = NigeriaPeopleRegistrationService.get_mapping(registration.mapping)
        individuals_key = mapping["defaults"].get("individuals_key", "individual-details")
        national_id_field_name = NigeriaPeopleRegistrationService._get_national_id_field_name(mapping)

        for record in records.iterator():
            record_data = record.get_data()
            individual_data = (record_data.get(individuals_key) or [{}])[0]
            writer.writerow(
                {
                    "record_id": record.id,
                    "source_id": record.source_id,
                    "registration": record.registration,
                    "timestamp": record.timestamp,
                    "ignored_reason": record.error_message or "",
                    "account_number": NigeriaPeopleRegistrationService._get_account_number_from_record_data(
                        record_data,
                        mapping,
                    ),
                    "national_id": individual_data.get(national_id_field_name, ""),
                    "given_name": individual_data.get("given_name_i_c", ""),
                    "middle_name": individual_data.get("middle_name_i_c", ""),
                    "family_name": individual_data.get("family_name_i_c", ""),
                    "phone_number": individual_data.get("phone_no_i_c", ""),
                }
            )

        return response
