from typing import TYPE_CHECKING, Any

from hope.models.account import Account
from hope.models.delivery_mechanism_config import DeliveryMechanismConfig
from hope.models.fsp_name_mapping import FspNameMapping
from hope.models.individual import Individual

if TYPE_CHECKING:
    from hope.models.delivery_mechanism import DeliveryMechanism
    from hope.models.financial_service_provider import FinancialServiceProvider


class PaymentDataCollector(Account):
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
    def delivery_data(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collector: "Individual",
    ) -> dict:
        delivery_data = {}
        account = collector.accounts.filter(account_type=delivery_mechanism.account_type).first()

        dm_configs = DeliveryMechanismConfig.objects.filter(fsp=fsp, delivery_mechanism=delivery_mechanism)
        collector_country = collector.household and collector.household.country
        if collector_country and (country_config := dm_configs.filter(country=collector_country).first()):
            dm_config = country_config
        else:
            dm_config = dm_configs.first()
        if not dm_config:
            return account.account_data if account else {}

        fsp_names_mappings = {x.external_name: x for x in fsp.names_mappings.all()}

        for field in dm_config.required_fields:
            if fsp_name_mapping := fsp_names_mappings.get(field):
                internal_field = fsp_name_mapping.hope_name
                associated_object = cls.get_associated_object(fsp_name_mapping.source, collector, account)
            else:
                internal_field = field
                associated_object = account.account_data if account else {}
            if isinstance(associated_object, dict):
                value = associated_object.get(internal_field, None)
                delivery_data[field] = value and str(value)
            else:
                delivery_data[field] = getattr(associated_object, internal_field, None)

        if account:
            if account.number:
                delivery_data["number"] = account.number
            if account.financial_institution:
                delivery_data["financial_institution"] = str(account.financial_institution.id)

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

        account = collector.accounts.filter(account_type=delivery_mechanism.account_type).first()

        fsp_names_mappings = {x.external_name: x for x in fsp.names_mappings.all()}
        dm_configs = DeliveryMechanismConfig.objects.filter(fsp=fsp, delivery_mechanism=delivery_mechanism)

        collector_country = collector.household and collector.household.country
        if collector_country and (country_config := dm_configs.filter(country=collector_country).first()):
            dm_config = country_config
        else:
            dm_config = dm_configs.first()
        if not dm_config:
            return True

        for field_value in dm_config.required_fields:
            field = field_value
            if fsp_name_mapping := fsp_names_mappings.get(field):
                field = fsp_name_mapping.hope_name
                associated_object = cls.get_associated_object(fsp_name_mapping.source, collector, account)
            else:
                associated_object = account.account_data if account else {}
            if isinstance(associated_object, dict):
                value = associated_object.get(field, None)
            else:
                value = getattr(associated_object, field, None)

            if value in [None, ""]:
                return False

        return True

    class Meta:
        app_label = "payment"
        proxy = True
        verbose_name = "Payment Data Collector"
        verbose_name_plural = "Payment Data Collectors"
