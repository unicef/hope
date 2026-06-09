from typing import TYPE_CHECKING, Any

from hope.models.account import Account
from hope.models.delivery_mechanism_config import DeliveryMechanismConfig
from hope.models.financial_institution_mapping import FinancialInstitutionMapping
from hope.models.fsp_name_mapping import FspNameMapping
from hope.models.individual import Individual

if TYPE_CHECKING:
    from hope.models.delivery_mechanism import DeliveryMechanism
    from hope.models.financial_service_provider import FinancialServiceProvider


class PaymentDataCollector(Account):
    SERVICE_PROVIDER_CODE = "service_provider_code"

    @classmethod
    def get_associated_object(
        cls,
        associated_with: str,
        collector: Individual,
        account: Account | None = None,
    ) -> Any:
        associated_objects = {
            FspNameMapping.SourceModel.INDIVIDUAL.value: collector,
            FspNameMapping.SourceModel.HOUSEHOLD.value: collector.household,
            FspNameMapping.SourceModel.ACCOUNT.value: account.account_data if account else {},
        }
        return associated_objects.get(associated_with)

    @classmethod
    def get_delivery_mechanism_config(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collector: Individual,
    ) -> DeliveryMechanismConfig | None:
        dm_configs = DeliveryMechanismConfig.objects.filter(fsp=fsp, delivery_mechanism=delivery_mechanism)
        collector_country = collector.household and collector.household.country
        if collector_country and (country_config := dm_configs.filter(country=collector_country).first()):
            return country_config
        return dm_configs.first()

    @classmethod
    def resolve_financial_institution_code(
        cls,
        fsp: "FinancialServiceProvider",
        account: Account | None,
    ) -> str | None:
        if not account or not account.financial_institution:
            return None

        financial_institution = account.financial_institution
        if financial_institution.is_generic:
            return None

        return FinancialInstitutionMapping.objects.filter(
            financial_institution=financial_institution,
            financial_service_provider=fsp,
        ).values_list("code", flat=True).first()

    @classmethod
    def resolve_required_field(
        cls,
        fsp: "FinancialServiceProvider",
        collector: Individual,
        account: Account | None,
        output_field: str,
        fsp_name_mapping: FspNameMapping | None,
    ) -> Any:
        if fsp_name_mapping:
            internal_field = fsp_name_mapping.hope_name
            associated_object = cls.get_associated_object(fsp_name_mapping.source, collector, account)
        else:
            internal_field = output_field
            associated_object = account.account_data if account else {}

        if isinstance(associated_object, dict):
            value = associated_object.get(internal_field, None)
        else:
            value = getattr(associated_object, internal_field, None)

        if cls.SERVICE_PROVIDER_CODE in (output_field, internal_field):
            financial_institution_code = cls.resolve_financial_institution_code(fsp, account)
            if financial_institution_code not in [None, ""]:
                return financial_institution_code

        return value

    @classmethod
    def delivery_data(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collector: "Individual",
    ) -> dict:
        delivery_data = {}
        account = (
            collector.accounts.select_related("financial_institution")
            .filter(account_type=delivery_mechanism.account_type)
            .first()
        )

        dm_config = cls.get_delivery_mechanism_config(fsp, delivery_mechanism, collector)
        if not dm_config:
            return account.account_data if account else {}

        fsp_names_mappings = {x.external_name: x for x in fsp.names_mappings.all()}

        for field in dm_config.required_fields:
            value = cls.resolve_required_field(fsp, collector, account, field, fsp_names_mappings.get(field))
            delivery_data[field] = value and str(value)

        if account:
            delivery_data.setdefault("number", account.number)
            delivery_data.setdefault("financial_institution_name", getattr(account.financial_institution, "name", ""))
            delivery_data.setdefault("financial_institution_pk", str(getattr(account.financial_institution, "pk", "")))

        return delivery_data

    @classmethod
    def validate_account(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collector: Individual,
    ) -> bool:
        if not delivery_mechanism.account_type:
            # ex. "cash" - doesn't need any validation
            return True

        account = (
            collector.accounts.select_related("financial_institution")
            .filter(account_type=delivery_mechanism.account_type)
            .first()
        )

        fsp_names_mappings = {x.external_name: x for x in fsp.names_mappings.all()}
        dm_config = cls.get_delivery_mechanism_config(fsp, delivery_mechanism, collector)
        if not dm_config:
            return True

        for field_value in dm_config.required_fields:
            value = cls.resolve_required_field(
                fsp,
                collector,
                account,
                field_value,
                fsp_names_mappings.get(field_value),
            )

            if value in [None, ""]:
                return False

        return True

    class Meta:
        app_label = "payment"
        proxy = True
        verbose_name = "Payment Data Collector"
        verbose_name_plural = "Payment Data Collectors"
