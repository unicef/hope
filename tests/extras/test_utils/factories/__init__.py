"""Factories for tests."""

from .account import (
    AdminAreaLimitedToFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from .accountability import CommunicationMessageFactory, FeedbackFactory, FeedbackMessageFactory, SurveyFactory
from .api import APITokenFactory
from .changelog import ChangelogFactory
from .core import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    CountryCodeMapFactory,
    DataCollectingTypeFactory,
    FileTempFactory,
    FlexibleAttributeChoiceFactory,
    FlexibleAttributeFactory,
    PeriodicFieldDataFactory,
    XLSXKoboTemplateFactory,
)
from .geo import AreaFactory, AreaTypeFactory, CountryFactory
from .grievance import GrievanceTicketFactory
from .household import (
    DocumentFactory,
    DocumentTypeFactory,
    EntitlementCardFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from .payment import (
    AccountFactory,
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialInstitutionFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    WesternUnionInvoiceFactory,
    WesternUnionPaymentPlanReportFactory,
)
from .program import ProgramCycleFactory, ProgramFactory
from .registration_data import ImportDataFactory, RegistrationDataImportFactory
from .steficon import RuleCommitFactory, RuleFactory

__all__ = [
    "AdminAreaLimitedToFactory",
    "APITokenFactory",
    "AreaFactory",
    "AreaTypeFactory",
    "BeneficiaryGroupFactory",
    "BusinessAreaFactory",
    "ChangelogFactory",
    "CommunicationMessageFactory",
    "CountryFactory",
    "CountryCodeMapFactory",
    "DataCollectingTypeFactory",
    "FileTempFactory",
    "FeedbackFactory",
    "FeedbackMessageFactory",
    "FlexibleAttributeChoiceFactory",
    "FlexibleAttributeFactory",
    "GrievanceTicketFactory",
    "DocumentFactory",
    "DocumentTypeFactory",
    "EntitlementCardFactory",
    "HouseholdFactory",
    "ImportDataFactory",
    "IndividualFactory",
    "IndividualRoleInHouseholdFactory",
    "AccountFactory",
    "AccountTypeFactory",
    "DeliveryMechanismFactory",
    "FinancialInstitutionFactory",
    "FinancialServiceProviderFactory",
    "FspXlsxTemplatePerDeliveryMechanismFactory",
    "FinancialServiceProviderXlsxTemplateFactory",
    "PartnerFactory",
    "PaymentFactory",
    "PaymentHouseholdSnapshotFactory",
    "PaymentPlanFactory",
    "PaymentVerificationFactory",
    "PaymentVerificationPlanFactory",
    "PaymentVerificationSummaryFactory",
    "PeriodicFieldDataFactory",
    "ProgramCycleFactory",
    "ProgramFactory",
    "RegistrationDataImportFactory",
    "RoleAssignmentFactory",
    "RoleFactory",
    "RuleCommitFactory",
    "RuleFactory",
    "SurveyFactory",
    "UserFactory",
    "WesternUnionInvoiceFactory",
    "WesternUnionPaymentPlanReportFactory",
    "XLSXKoboTemplateFactory",
]
