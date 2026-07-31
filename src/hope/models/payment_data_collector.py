from collections.abc import Iterable
from typing import TYPE_CHECKING, Any
from uuid import UUID

from hope.models.account import Account
from hope.models.delivery_mechanism_config import DeliveryMechanismConfig
from hope.models.financial_institution_mapping import FinancialInstitutionMapping
from hope.models.fsp_name_mapping import FspNameMapping
from hope.models.individual import Individual

if TYPE_CHECKING:
    from hope.models.delivery_mechanism import DeliveryMechanism
    from hope.models.financial_service_provider import FinancialServiceProvider

type PaymentDeliveryData = dict[str, object]
type DeliveryDataByCollector = dict[UUID, PaymentDeliveryData]
type AccountValidityByCollector = dict[UUID, bool]


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

        return (
            FinancialInstitutionMapping.objects.filter(
                financial_institution=financial_institution,
                financial_service_provider=fsp,
            )
            .values_list("code", flat=True)
            .first()
        )

    @classmethod
    def resolve_required_field(
        cls,
        fsp: "FinancialServiceProvider",
        collector: Individual,
        account: Account | None,
        output_field: str,
        fsp_name_mapping: FspNameMapping | None,
    ) -> Any:
        internal_field = fsp_name_mapping.hope_name if fsp_name_mapping else output_field
        financial_institution_code = (
            cls.resolve_financial_institution_code(fsp, account)
            if cls.SERVICE_PROVIDER_CODE in (output_field, internal_field)
            else None
        )
        return cls._resolve_required_field_value(
            collector,
            account,
            output_field,
            fsp_name_mapping,
            financial_institution_code,
        )

    @classmethod
    def _resolve_required_field_value(
        cls,
        collector: Individual,
        account: Account | None,
        output_field: str,
        fsp_name_mapping: FspNameMapping | None,
        financial_institution_code: str | None,
    ) -> object:
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

        if cls.SERVICE_PROVIDER_CODE in (output_field, internal_field) and financial_institution_code not in [None, ""]:
            return financial_institution_code

        return value

    @classmethod
    def _process_collectors(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collectors: Iterable[Individual],
    ) -> tuple[DeliveryDataByCollector, AccountValidityByCollector]:
        collectors = list(collectors)
        delivery_data_by_collector: DeliveryDataByCollector = {}
        validity_by_collector: AccountValidityByCollector = {}

        accounts_by_individual_id: dict[UUID, Account] = {}
        if delivery_mechanism.account_type_id:
            accounts = (
                Account.objects.filter(
                    individual_id__in={collector.id for collector in collectors},
                    account_type_id=delivery_mechanism.account_type_id,
                )
                .select_related("financial_institution")
                .order_by("individual_id", "-created_at")
            )
            for loaded_account in accounts:
                accounts_by_individual_id.setdefault(loaded_account.individual_id, loaded_account)

        configs = list(DeliveryMechanismConfig.objects.filter(fsp=fsp, delivery_mechanism=delivery_mechanism))
        default_config = configs[0] if configs else None
        mappings = {mapping.external_name: mapping for mapping in fsp.names_mappings.all()}
        financial_institution_ids: set[int] = {
            account.financial_institution_id
            for account in accounts_by_individual_id.values()
            if account.financial_institution_id and not account.financial_institution.is_generic
        }
        financial_institution_codes: dict[int, str] = (
            dict(
                FinancialInstitutionMapping.objects.filter(
                    financial_service_provider=fsp,
                    financial_institution_id__in=financial_institution_ids,
                ).values_list("financial_institution_id", "code")
            )
            if financial_institution_ids
            else {}
        )

        for collector in collectors:
            account = accounts_by_individual_id.get(collector.id)
            country_id = collector.household.country_id if collector.household else None
            config = next(
                (config for config in configs if country_id and config.country_id == country_id),
                default_config,
            )
            if not config:
                delivery_data_by_collector[collector.id] = account.account_data if account else {}
                validity_by_collector[collector.id] = True
                continue

            resolved_fields: PaymentDeliveryData = {}
            for field in config.required_fields:
                mapping = mappings.get(field)
                internal_field = mapping.hope_name if mapping else field
                financial_institution_id = account.financial_institution_id if account else None
                financial_institution_code = (
                    financial_institution_codes.get(financial_institution_id)
                    if financial_institution_id is not None and cls.SERVICE_PROVIDER_CODE in (field, internal_field)
                    else None
                )
                value = cls._resolve_required_field_value(
                    collector,
                    account,
                    field,
                    mapping,
                    financial_institution_code,
                )
                resolved_fields[field] = value

            validity_by_collector[collector.id] = all(value not in [None, ""] for value in resolved_fields.values())
            delivery_data = {field: value and str(value) for field, value in resolved_fields.items()}
            if account:
                delivery_data.setdefault("number", account.number)
                delivery_data.setdefault(
                    "financial_institution_name", getattr(account.financial_institution, "name", "")
                )
                delivery_data.setdefault(
                    "financial_institution_pk", str(getattr(account.financial_institution, "pk", ""))
                )
            delivery_data_by_collector[collector.id] = delivery_data
        return delivery_data_by_collector, validity_by_collector

    @classmethod
    def delivery_data_for_collectors(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collectors: Iterable[Individual],
    ) -> DeliveryDataByCollector:
        delivery_data_by_collector, _ = cls._process_collectors(fsp, delivery_mechanism, collectors)
        return delivery_data_by_collector

    @classmethod
    def validate_accounts(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collectors: Iterable[Individual],
    ) -> AccountValidityByCollector:
        if not delivery_mechanism.account_type_id:
            return {collector.id: True for collector in collectors}
        _, validity_by_collector = cls._process_collectors(fsp, delivery_mechanism, collectors)
        return validity_by_collector

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
            value = cls.resolve_required_field(
                fsp,
                collector,
                account,
                field,
                fsp_names_mappings.get(field),
            )
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
