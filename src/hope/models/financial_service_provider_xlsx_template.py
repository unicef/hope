from typing import Any

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory, get_core_fields_attributes
from hope.apps.core.field_attributes.fields_types import _HOUSEHOLD, _INDIVIDUAL
from hope.apps.payment.fields import DynamicChoiceArrayField
from hope.models.area import Area
from hope.models.country import Country
from hope.models.document_type import DocumentType
from hope.models.flexible_attribute import FlexibleAttribute
from hope.models.payment import Payment, logger
from hope.models.utils import TimeStampedUUIDModel


class FlexFieldArrayField(ArrayField):
    def formfield(
        self,
        form_class: Any | None = ...,
        choices_form_class: Any | None = ...,
        **kwargs: Any,
    ) -> Any:
        widget = FilteredSelectMultiple(self.verbose_name, False)
        # TODO exclude PDU here
        flexible_attributes = FlexibleAttribute.objects.values_list("name", flat=True)
        flexible_choices = ((x, x) for x in flexible_attributes)
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": widget,
            "choices": flexible_choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class FinancialServiceProviderXlsxTemplate(TimeStampedUUIDModel):
    COLUMNS_CHOICES = (
        ("payment_id", _("Payment ID")),
        ("household_id", _("Household ID")),
        ("individual_id", _("Individual ID")),
        ("household_size", _("Household Size")),
        ("collector_name", _("Collector Name")),
        ("alternate_collector_full_name", _("Alternate collector Full Name")),
        ("alternate_collector_given_name", _("Alternate collector Given Name")),
        ("alternate_collector_family_name", _("Alternate collector Family Name")),
        ("alternate_collector_middle_name", _("Alternate collector Middle Name")),
        ("alternate_collector_phone_no", _("Alternate collector phone number")),
        (
            "alternate_collector_document_numbers",
            _("Alternate collector Document numbers"),
        ),
        ("alternate_collector_sex", _("Alternate collector Gender")),
        ("payment_channel", _("Payment Channel")),
        ("fsp_name", _("FSP Name")),
        ("currency", _("Currency")),
        ("entitlement_quantity", _("Entitlement Quantity")),
        ("entitlement_quantity_usd", _("Entitlement Quantity USD")),
        ("delivered_quantity", _("Delivered Quantity")),
        ("delivery_date", _("Delivery Date")),
        ("reference_id", _("Reference id")),
        ("reason_for_unsuccessful_payment", _("Reason for unsuccessful payment")),
        ("order_number", _("Order Number")),
        ("token_number", _("Token Number")),
        ("additional_collector_name", _("Additional Collector Name")),
        ("additional_document_type", _("Additional Document Type")),
        ("additional_document_number", _("Additional Document Number")),
        ("registration_token", _("Registration Token")),
        ("status", _("Status")),
        (
            "transaction_status_blockchain_link",
            _("Transaction Status on the Blockchain"),
        ),
        ("fsp_auth_code", _("Auth Code")),
        ("account_data", _("Account Data")),
    )

    DEFAULT_COLUMNS = [col[0] for col in COLUMNS_CHOICES]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_financial_service_provider_xlsx_templates",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    name = models.CharField(max_length=120, verbose_name=_("Name"))
    columns = MultiSelectField(
        max_length=1000,
        choices=COLUMNS_CHOICES,
        default=DEFAULT_COLUMNS,
        verbose_name=_("Columns"),
        help_text=_("Select the columns to include in the report"),
    )
    core_fields = DynamicChoiceArrayField(
        models.CharField(max_length=255, blank=True),
        choices_callable=FieldFactory.get_all_core_fields_choices,
        default=list,
        blank=True,
    )
    flex_fields = FlexFieldArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
    )
    document_types = DynamicChoiceArrayField(
        models.CharField(max_length=255, blank=True),
        choices_callable=DocumentType.get_all_doc_types_choices,
        default=list,
        blank=True,
    )

    class Meta:
        app_label = "payment"

    @staticmethod
    def get_data_from_payment_snapshot(
        household_data: dict[str, Any],
        core_field: dict[str, Any],
    ) -> str | None:
        collector_data = household_data.get("primary_collector") or household_data.get("alternate_collector") or {}
        primary_collector = household_data.get("primary_collector", {})
        alternate_collector = household_data.get("alternate_collector", {})

        lookup = core_field["lookup"]
        main_key = None  # just help find specific field from snapshot
        snapshot_field_path = core_field.get("snapshot_field")
        if snapshot_field_path:
            snapshot_field_path_split = snapshot_field_path.split("__")
            main_key = snapshot_field_path.split("__")[0] if len(snapshot_field_path_split) > 0 else None

            if main_key in {"country_origin_id", "country_id"}:
                country = Country.objects.filter(pk=household_data.get(main_key)).first()
                return country.iso_code3 if country else None

            if main_key in {"admin1_id", "admin2_id", "admin3_id", "admin4_id"}:
                area = Area.objects.filter(pk=household_data.get(main_key)).first()
                return f"{area.p_code} - {area.name}" if area else "" if area else None

            if main_key == "roles":
                lookup_id = primary_collector.get("id") or alternate_collector.get("id")
                if not lookup_id:
                    return None

                for role in household_data.get("roles", []):
                    individual = role.get("individual", {})
                    if individual.get("id") == lookup_id:
                        return role.get("role")
                # return None if role not found
                return None

            if main_key in {"primary_collector", "alternate_collector"}:
                return household_data.get(main_key, {}).get("id")

            if main_key == "documents":
                doc_type, doc_lookup = (
                    snapshot_field_path_split[1],
                    snapshot_field_path_split[2],
                )
                documents_list = collector_data.get("documents", [])
                documents_dict = {doc.get("type"): doc for doc in documents_list}
                return documents_dict.get(doc_type, {}).get(doc_lookup)

        if core_field["associated_with"] == _INDIVIDUAL:
            return collector_data.get(lookup, None) or collector_data.get(main_key, None)

        if core_field["associated_with"] == _HOUSEHOLD:
            return household_data.get(lookup)

        return None

    @staticmethod
    def get_column_from_core_field(
        payment: "Payment",
        core_field_name: str,
    ) -> Any:
        core_fields_attributes = FieldFactory(get_core_fields_attributes()).to_dict_by("name")
        core_field = core_fields_attributes.get(core_field_name)
        if not core_field:
            # Some fields can be added to the template, such as 'size'
            # which are not applicable to "People" export.
            return None

        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.warning(f"Not found snapshot for Payment {payment.unicef_id}")
            return None

        return FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(snapshot.snapshot_data, core_field)

    @classmethod
    def get_column_value_from_payment(cls, payment: "Payment", column_name: str) -> str | float | list | None:
        # we can get if needed payment.parent.program.is_social_worker_program
        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.warning(f"Not found snapshot for Payment {payment.unicef_id}")
            return None
        snapshot_data = snapshot.snapshot_data
        primary_collector = snapshot_data.get("primary_collector", {})
        alternate_collector = snapshot_data.get("alternate_collector", {})
        collector_data = primary_collector or alternate_collector or {}

        map_obj_name_column = {
            "payment_id": (payment, "unicef_id"),
            "individual_id": (collector_data, "unicef_id"),  # add for people export
            "household_id": (snapshot_data, "unicef_id"),  # remove for people export
            "household_size": (snapshot_data, "size"),  # remove for people export
            "admin_level_2": (snapshot_data, "admin2"),
            "village": (snapshot_data, "village"),
            "collector_name": (collector_data, "full_name"),
            "alternate_collector_full_name": (alternate_collector, "full_name"),
            "alternate_collector_given_name": (alternate_collector, "given_name"),
            "alternate_collector_middle_name": (alternate_collector, "middle_name"),
            "alternate_collector_family_name": (alternate_collector, "family_name"),
            "alternate_collector_sex": (alternate_collector, "sex"),
            "alternate_collector_phone_no": (alternate_collector, "phone_no"),
            "alternate_collector_document_numbers": (
                alternate_collector,
                "document_number",
            ),
            "payment_channel": (payment.delivery_type, "name"),
            "fsp_name": (payment.financial_service_provider, "name"),
            "currency": (payment, "currency"),
            "entitlement_quantity": (payment, "entitlement_quantity"),
            "entitlement_quantity_usd": (payment, "entitlement_quantity_usd"),
            "delivered_quantity": (payment, "delivered_quantity"),
            "delivery_date": (payment, "delivery_date"),
            "reference_id": (payment, "transaction_reference_id"),
            "reason_for_unsuccessful_payment": (
                payment,
                "reason_for_unsuccessful_payment",
            ),
            "order_number": (payment, "order_number"),
            "token_number": (payment, "token_number"),
            "additional_collector_name": (payment, "additional_collector_name"),
            "additional_document_type": (payment, "additional_document_type"),
            "additional_document_number": (payment, "additional_document_number"),
            "status": (payment, "payment_status"),
            "transaction_status_blockchain_link": (
                payment,
                "transaction_status_blockchain_link",
            ),
            "fsp_auth_code": (payment, "fsp_auth_code"),
        }
        additional_columns = {
            "admin_level_2": (cls.get_admin_level_2, [snapshot_data]),
            "alternate_collector_document_numbers": (
                cls.get_alternate_collector_doc_numbers,
                [snapshot_data],
            ),
        }
        if column_name in DocumentType.get_all_doc_types():
            return cls.get_document_number_by_doc_type_key(snapshot_data, column_name)

        if column_name in additional_columns:
            method, args = additional_columns[column_name]
            return method(*args)

        if column_name not in map_obj_name_column:
            return "wrong_column_name"
        if column_name == "delivered_quantity" and payment.status == Payment.STATUS_ERROR:  # Unsuccessful Payment
            return float(-1)
        if column_name == "delivery_date" and payment.delivery_date is not None:
            return str(payment.delivery_date)

        obj, nested_field = map_obj_name_column[column_name]
        # return if obj is dictionary from snapshot
        if isinstance(obj, dict):
            return obj.get(nested_field, "")
        # return if obj is model
        return getattr(obj, nested_field, None) or ""

    @classmethod
    def get_account_value_from_payment(cls, payment: "Payment", key_name: str) -> str | float | list | None:
        """Get Account values from Collector's Account.data."""
        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.warning(f"Not found snapshot for Payment {payment.unicef_id}")
            return None
        snapshot_data = snapshot.snapshot_data
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or {}
        )
        account_data = collector_data.get("account_data", {})
        return account_data.get(key_name, "")

    @staticmethod
    def get_document_number_by_doc_type_key(snapshot_data: dict[str, Any], document_type_key: str) -> str:
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or {}
        )
        documents_list = collector_data.get("documents", [])
        documents_dict = {doc.get("type"): doc for doc in documents_list}
        return documents_dict.get(document_type_key, {}).get("document_number", "")

    @staticmethod
    def get_alternate_collector_doc_numbers(snapshot_data: dict[str, Any]) -> str:
        alternate_collector_data = snapshot_data.get("alternate_collector", {}) or {}
        doc_list = alternate_collector_data.get("documents", [])
        doc_numbers = [doc.get("document_number", "") for doc in doc_list]
        return ", ".join(doc_numbers)

    @staticmethod
    def get_admin_level_2(snapshot_data: dict[str, Any]) -> str:
        area = Area.objects.filter(pk=snapshot_data.get("admin2_id")).first()
        return area.name if area else ""

    def __str__(self) -> str:
        return f"{self.name} ({len(self.columns) + len(self.core_fields)})"
