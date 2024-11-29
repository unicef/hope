import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_fsm import FSMField, transition
from multiselectfield import MultiSelectField

from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
    FieldFactory,
    get_core_fields_attributes,
)
from hct_mis_api.apps.core.field_attributes.fields_types import (
    _DELIVERY_MECHANISM_DATA,
    _HOUSEHOLD,
    _INDIVIDUAL,
)
from hct_mis_api.apps.core.mixins import LimitBusinessAreaModelMixin
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.payment.fields import DynamicChoiceArrayField
from hct_mis_api.apps.payment.models.delivery_mechanism_models import (
    DeliveryMechanismData,
)
from hct_mis_api.apps.payment.models.payment_model import Payment
from hct_mis_api.apps.utils.models import InternalDataFieldModel, TimeStampedUUIDModel

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User

logger = logging.getLogger(__name__)


class FlexFieldArrayField(ArrayField):
    def formfield(self, form_class: Optional[Any] = ..., choices_form_class: Optional[Any] = ..., **kwargs: Any) -> Any:
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
        ("alternate_collector_middle_name", _("Alternate collector Middle Name")),
        ("alternate_collector_phone_no", _("Alternate collector phone number")),
        ("alternate_collector_document_numbers", _("Alternate collector Document numbers")),
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
        ("transaction_status_blockchain_link", _("Transaction Status on the Blockchain")),
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

    @staticmethod
    def get_data_from_payment_snapshot(
        household_data: Dict[str, Any],
        core_field: Dict[str, Any],
        delivery_mechanism_data: Optional["DeliveryMechanismData"] = None,
    ) -> Optional[str]:
        core_field_name = core_field["name"]
        collector_data = household_data.get("primary_collector") or household_data.get("alternate_collector") or dict()
        primary_collector = household_data.get("primary_collector", {})
        alternate_collector = household_data.get("alternate_collector", {})

        if delivery_mechanism_data and core_field["associated_with"] == _DELIVERY_MECHANISM_DATA:
            delivery_mech_data = collector_data.get("delivery_mechanisms_data", {}).get(
                delivery_mechanism_data.delivery_mechanism.code, {}
            )
            return delivery_mech_data.get(core_field_name, None)

        lookup = core_field["lookup"]
        main_key = None  # just help find specific field from snapshot
        snapshot_field_path = core_field.get("snapshot_field")
        if snapshot_field_path:
            snapshot_field_path_split = snapshot_field_path.split("__")
            main_key = snapshot_field_path.split("__")[0] if len(snapshot_field_path_split) > 0 else None

            if main_key in {"country_origin_id", "country_id"}:
                country = Country.objects.filter(pk=household_data.get(main_key)).first()
                return country.iso_code3 if country else None

            if main_key in {"admin1_id", "admin2_id", "admin3_id", "admin4_id", "admin_area_id"}:
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

            if main_key == "bank_account_info":
                bank_account_info_lookup = snapshot_field_path_split[1]
                return collector_data.get("bank_account_info", {}).get(bank_account_info_lookup)

            if main_key == "documents":
                doc_type, doc_lookup = snapshot_field_path_split[1], snapshot_field_path_split[2]
                documents_list = collector_data.get("documents", [])
                documents_dict = {doc.get("type"): doc for doc in documents_list}
                return documents_dict.get(doc_type, {}).get(doc_lookup)

        if core_field["associated_with"] == _INDIVIDUAL:
            return collector_data.get(lookup, None) or collector_data.get(main_key, None)

        if core_field["associated_with"] == _HOUSEHOLD:
            return household_data.get(lookup, None)

        return None

    @staticmethod
    def get_column_from_core_field(
        payment: "Payment",
        core_field_name: str,
        delivery_mechanism_data: Optional["DeliveryMechanismData"] = None,
    ) -> Any:
        core_fields_attributes = FieldFactory(get_core_fields_attributes()).to_dict_by("name")
        core_field = core_fields_attributes.get(core_field_name)
        if not core_field:
            # Some fields can be added to the template, such as 'size' or 'collect_individual_data'
            # which are not applicable to "People" export.
            return None

        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.error(f"Not found snapshot for Payment {payment.unicef_id}")
            return None

        snapshot_data = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
            snapshot.snapshot_data, core_field, delivery_mechanism_data
        )

        return snapshot_data

    @classmethod
    def get_column_value_from_payment(cls, payment: "Payment", column_name: str) -> Union[str, float, list, None]:
        # we can get if needed payment.parent.program.is_social_worker_program
        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.error(f"Not found snapshot for Payment {payment.unicef_id}")
            return None
        snapshot_data = snapshot.snapshot_data
        primary_collector = snapshot_data.get("primary_collector", {})
        alternate_collector = snapshot_data.get("alternate_collector", {})
        collector_data = primary_collector or alternate_collector or dict()

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
            "alternate_collector_sex": (alternate_collector, "sex"),
            "alternate_collector_phone_no": (alternate_collector, "phone_no"),
            "alternate_collector_document_numbers": (alternate_collector, "document_number"),
            "payment_channel": (payment.delivery_type, "name"),
            "fsp_name": (payment.financial_service_provider, "name"),
            "currency": (payment, "currency"),
            "entitlement_quantity": (payment, "entitlement_quantity"),
            "entitlement_quantity_usd": (payment, "entitlement_quantity_usd"),
            "delivered_quantity": (payment, "delivered_quantity"),
            "delivery_date": (payment, "delivery_date"),
            "reference_id": (payment, "transaction_reference_id"),
            "reason_for_unsuccessful_payment": (payment, "reason_for_unsuccessful_payment"),
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
        }
        additional_columns = {
            "registration_token": cls.get_registration_token_doc_number,
            "national_id": cls.get_national_id_doc_number,
            "admin_level_2": cls.get_admin_level_2,
            "alternate_collector_document_numbers": cls.get_alternate_collector_doc_numbers,
        }
        if column_name in additional_columns:
            method = additional_columns[column_name]
            return method(snapshot_data)

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

    @staticmethod
    def get_registration_token_doc_number(snapshot_data: Dict[str, Any]) -> str:
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or dict()
        )
        documents_list = collector_data.get("documents", [])
        documents_dict = {doc.get("type"): doc for doc in documents_list}
        return documents_dict.get("registration_token", {}).get("document_number", "")

    @staticmethod
    def get_national_id_doc_number(snapshot_data: Dict[str, Any]) -> str:
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or dict()
        )
        documents_list = collector_data.get("documents", [])
        documents_dict = {doc.get("type"): doc for doc in documents_list}
        return documents_dict.get("national_id", {}).get("document_number", "")

    @staticmethod
    def get_alternate_collector_doc_numbers(snapshot_data: Dict[str, Any]) -> str:
        alternate_collector_data = snapshot_data.get("alternate_collector", {}) or dict()
        doc_list = alternate_collector_data.get("documents", [])
        doc_numbers = [doc.get("document_number", "") for doc in doc_list]
        return ", ".join(doc_numbers)

    @staticmethod
    def get_admin_level_2(snapshot_data: Dict[str, Any]) -> str:
        area = Area.objects.filter(pk=snapshot_data.get("admin2_id")).first()
        return area.name if area else ""

    def __str__(self) -> str:
        return f"{self.name} ({len(self.columns) + len(self.core_fields)})"


class FspXlsxTemplatePerDeliveryMechanism(TimeStampedUUIDModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_fsp_xlsx_template_per_delivery_mechanisms",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    financial_service_provider = models.ForeignKey(
        "FinancialServiceProvider", on_delete=models.CASCADE, related_name="fsp_xlsx_template_per_delivery_mechanisms"
    )
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    xlsx_template = models.ForeignKey(
        "FinancialServiceProviderXlsxTemplate",
        on_delete=models.CASCADE,
        related_name="fsp_xlsx_template_per_delivery_mechanisms",
    )

    class Meta:
        unique_together = ("financial_service_provider", "delivery_mechanism")

    def __str__(self) -> str:
        return f"{self.financial_service_provider.name} - {self.xlsx_template} - {self.delivery_mechanism}"  # pragma: no cover


class FinancialServiceProvider(InternalDataFieldModel, LimitBusinessAreaModelMixin, TimeStampedUUIDModel):
    COMMUNICATION_CHANNEL_API = "API"
    COMMUNICATION_CHANNEL_SFTP = "SFTP"
    COMMUNICATION_CHANNEL_XLSX = "XLSX"
    COMMUNICATION_CHANNEL_CHOICES = (
        (COMMUNICATION_CHANNEL_API, "API"),
        (COMMUNICATION_CHANNEL_SFTP, "SFTP"),
        (COMMUNICATION_CHANNEL_XLSX, "XLSX"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_financial_service_providers",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    name = models.CharField(max_length=100, unique=True)
    vision_vendor_number = models.CharField(max_length=100, unique=True)
    delivery_mechanisms = models.ManyToManyField("payment.DeliveryMechanism")
    distribution_limit = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True,
        help_text="The maximum amount of money in USD that can be distributed or unlimited if null",
        db_index=True,
    )
    communication_channel = models.CharField(max_length=6, choices=COMMUNICATION_CHANNEL_CHOICES, db_index=True)
    data_transfer_configuration = models.JSONField(
        help_text="JSON configuration for the data transfer mechanism",
        null=True,
        blank=True,
        default=dict,
    )
    xlsx_templates = models.ManyToManyField(
        "payment.FinancialServiceProviderXlsxTemplate",
        through="FspXlsxTemplatePerDeliveryMechanism",
        related_name="financial_service_providers",
    )
    payment_gateway_id = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.vision_vendor_number}): {self.communication_channel}"

    def get_xlsx_template(self, delivery_mechanism: str) -> Optional["FinancialServiceProviderXlsxTemplate"]:
        try:
            return self.xlsx_templates.get(
                fsp_xlsx_template_per_delivery_mechanisms__delivery_mechanism=delivery_mechanism
            )
        except FinancialServiceProviderXlsxTemplate.DoesNotExist:
            return None

    def can_accept_any_volume(self) -> bool:
        from hct_mis_api.apps.payment.models import PaymentPlan

        if (
            self.distribution_limit is not None
            and self.delivery_mechanisms_per_payment_plan.filter(
                payment_plan__status__in=[
                    PaymentPlan.Status.LOCKED_FSP,
                    PaymentPlan.Status.IN_APPROVAL,
                    PaymentPlan.Status.IN_AUTHORIZATION,
                    PaymentPlan.Status.IN_REVIEW,
                    PaymentPlan.Status.ACCEPTED,
                ]
            ).exists()
        ):
            return False

        if self.distribution_limit == 0.0:
            return False

        return True

    def can_accept_volume(self, volume: Decimal) -> bool:
        if self.distribution_limit is None:
            return True

        return volume <= self.distribution_limit

    @property
    def is_payment_gateway(self) -> bool:
        return self.communication_channel == self.COMMUNICATION_CHANNEL_API and self.payment_gateway_id is not None

    @property
    def configurations(self) -> List[Optional[dict]]:
        return []  # temporary disabled
        if not self.is_payment_gateway:
            return []
        return [
            {"key": config.get("key", None), "label": config.get("label", None), "id": config.get("id", None)}
            for config in self.data_transfer_configuration
        ]


class DeliveryMechanismPerPaymentPlan(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        NOT_SENT = "NOT_SENT"
        SENT = "SENT"

    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="delivery_mechanisms",
    )
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider",
        on_delete=models.PROTECT,
        related_name="delivery_mechanisms_per_payment_plan",
        null=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_delivery_mechanisms",
    )
    sent_date = models.DateTimeField()
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_delivery_mechanisms",
        null=True,
    )
    status = FSMField(default=Status.NOT_SENT, protected=False, db_index=True)
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    delivery_mechanism_order = models.PositiveIntegerField()

    sent_to_payment_gateway = models.BooleanField(default=False)
    chosen_configuration = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment_plan", "delivery_mechanism", "delivery_mechanism_order"],
                name="unique payment_plan_delivery_mechanism",
            ),
        ]

    @transition(
        field=status,
        source=Status.NOT_SENT,
        target=Status.SENT,
    )
    def status_send(self, sent_by: "User") -> None:
        self.sent_date = timezone.now()
        self.sent_by = sent_by
