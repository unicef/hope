"""Payment-related factories."""

from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import factory
from factory.django import DjangoModelFactory

from hope.models import (
    Account,
    AccountType,
    Approval,
    ApprovalProcess,
    DeliveryMechanism,
    FinancialInstitution,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    MergeStatusModel,
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentPlanSupportingDocument,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    WesternUnionInvoice,
    WesternUnionPaymentPlanReport,
)

from . import HouseholdFactory, IndividualFactory
from .account import UserFactory
from .core import BusinessAreaFactory
from .program import ProgramCycleFactory


class PaymentPlanFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlan

    status_date = factory.LazyFunction(timezone.now)
    status = PaymentPlan.Status.OPEN
    dispersion_start_date = factory.LazyFunction(date.today)
    dispersion_end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    program_cycle = factory.SubFactory(ProgramCycleFactory)
    created_by = factory.SubFactory(UserFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)

    @factory.post_generation
    def create_payment_verification_summary(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted is False:
            return
        if self.status == PaymentPlan.Status.FINISHED and not hasattr(self, "payment_verification_summary"):
            PaymentVerificationSummaryFactory(
                payment_plan=self,
            )


class ApprovalProcessFactory(DjangoModelFactory):
    class Meta:
        model = ApprovalProcess

    payment_plan = factory.SubFactory(PaymentPlanFactory)


class ApprovalFactory(DjangoModelFactory):
    class Meta:
        model = Approval

    approval_process = factory.SubFactory(ApprovalProcessFactory)
    type = Approval.APPROVAL
    created_by = factory.SubFactory(UserFactory)


class AccountTypeFactory(DjangoModelFactory):
    class Meta:
        model = AccountType

    key = factory.Sequence(lambda n: f"account_type_{n}")
    label = factory.Sequence(lambda n: f"Account Type {n}")
    unique_fields = []


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account

    number = factory.Sequence(lambda n: f"ACC-{n}")
    data = factory.LazyFunction(dict)
    individual = factory.SubFactory(IndividualFactory)
    account_type = factory.SubFactory(AccountTypeFactory)
    rdi_merge_status = MergeStatusModel.MERGED


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    parent = factory.SubFactory(PaymentPlanFactory)
    status_date = factory.LazyFunction(timezone.now)
    currency = "PLN"
    business_area = factory.SelfAttribute("parent.business_area")
    household = factory.SubFactory(
        HouseholdFactory,
        business_area=factory.SelfAttribute("..business_area"),
        program=factory.SelfAttribute("..parent.program"),
    )
    collector = factory.SubFactory(
        IndividualFactory,
        household=factory.SelfAttribute("..household"),
        business_area=factory.SelfAttribute("..household.business_area"),
        program=factory.SelfAttribute("..household.program"),
        registration_data_import=factory.SelfAttribute("..household.registration_data_import"),
    )


class PaymentHouseholdSnapshotFactory(DjangoModelFactory):
    class Meta:
        model = PaymentHouseholdSnapshot

    payment = factory.SubFactory(PaymentFactory)
    household_id = factory.LazyAttribute(lambda obj: obj.payment.household_id)
    snapshot_data = factory.LazyFunction(dict)


class PaymentVerificationSummaryFactory(DjangoModelFactory):
    class Meta:
        model = PaymentVerificationSummary


class PaymentPlanSplitFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlanSplit

    payment_plan = factory.SubFactory(PaymentPlanFactory)
    split_type = PaymentPlanSplit.SplitType.NO_SPLIT
    order = 0


class PaymentPlanSupportingDocumentFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlanSupportingDocument

    title = factory.Sequence(lambda n: f"Supporting Document {n}")
    payment_plan = factory.SubFactory(PaymentPlanFactory)
    file = factory.Sequence(
        lambda n: SimpleUploadedFile(f"supporting_doc_{n}.pdf", b"abc", content_type="application/pdf")
    )


class PaymentVerificationPlanFactory(DjangoModelFactory):
    class Meta:
        model = PaymentVerificationPlan

    payment_plan = factory.SubFactory(PaymentPlanFactory, status=PaymentPlan.Status.FINISHED)
    verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
    sampling = "FULL_LIST"


class PaymentVerificationFactory(DjangoModelFactory):
    class Meta:
        model = PaymentVerification

    payment_verification_plan = factory.SubFactory(
        PaymentVerificationPlanFactory,
    )
    payment = factory.SubFactory(
        PaymentFactory, parent=factory.SelfAttribute("..payment_verification_plan.payment_plan")
    )


class DeliveryMechanismFactory(DjangoModelFactory):
    class Meta:
        model = DeliveryMechanism

    code = factory.Sequence(lambda n: f"DM{n:04d}")
    name = factory.Sequence(lambda n: f"Delivery Mechanism {n}")
    payment_gateway_id = factory.Sequence(lambda n: f"dm-{n}")


class FinancialServiceProviderFactory(DjangoModelFactory):
    class Meta:
        model = FinancialServiceProvider

    name = factory.Sequence(lambda n: f"FSP {n}")
    vision_vendor_number = factory.Sequence(lambda n: f"VEN{n:04d}")
    communication_channel = FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX

    @factory.post_generation
    def delivery_mechanisms(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for delivery_mechanism in extracted:
                self.delivery_mechanisms.add(delivery_mechanism)


class FinancialServiceProviderXlsxTemplateFactory(DjangoModelFactory):
    class Meta:
        model = FinancialServiceProviderXlsxTemplate

    name = factory.Sequence(lambda n: f"FSP Template {n}")


class FspXlsxTemplatePerDeliveryMechanismFactory(DjangoModelFactory):
    class Meta:
        model = FspXlsxTemplatePerDeliveryMechanism

    financial_service_provider = factory.SubFactory(FinancialServiceProviderFactory)
    delivery_mechanism = factory.SubFactory(DeliveryMechanismFactory)
    xlsx_template = factory.SubFactory(FinancialServiceProviderXlsxTemplateFactory)


class WesternUnionInvoiceFactory(DjangoModelFactory):
    class Meta:
        model = WesternUnionInvoice

    name = factory.Sequence(lambda n: f"WU Invoice {n}")


class FinancialInstitutionFactory(DjangoModelFactory):
    class Meta:
        model = FinancialInstitution

    name = factory.Sequence(lambda n: f"Financial Institution {n}")
    type = FinancialInstitution.FinancialInstitutionType.BANK


class WesternUnionPaymentPlanReportFactory(DjangoModelFactory):
    class Meta:
        model = WesternUnionPaymentPlanReport

    qcf_file = factory.SubFactory(WesternUnionInvoiceFactory)
    payment_plan = factory.SubFactory(PaymentPlanFactory)
