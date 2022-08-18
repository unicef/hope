import logging
import math
import graphene

from decimal import Decimal

from django.contrib.admin.options import get_content_type_for_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.core.models import XLSXFileTemp
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanImportService import XlsxPaymentPlanImportService
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
)
from hct_mis_api.apps.payment.celery_tasks import (
    fsp_generate_xlsx_report_task,
    payment_plan_apply_steficon,
    import_payment_plan_payment_list_from_xlsx,
)
from hct_mis_api.apps.payment.inputs import (
    CreatePaymentVerificationInput,
    EditCashPlanPaymentVerificationInput,
    ActionPaymentPlanInput,
    CreateFinancialServiceProviderInput,
    CreatePaymentPlanInput,
    UpdatePaymentPlanInput,
)
from hct_mis_api.apps.payment.models import (
    PaymentVerification,
    PaymentPlan,
    DeliveryMechanismPerPaymentPlan,
    PaymentChannel,
    FinancialServiceProvider,
)
from hct_mis_api.apps.payment.schema import PaymentVerificationNode, FinancialServiceProviderNode, PaymentPlanNode
from hct_mis_api.apps.payment.services.fsp_service import FSPService
from hct_mis_api.apps.payment.services.verification_plan_crud_services import (
    VerificationPlanCrudServices,
)
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.payment.celery_tasks import create_cash_plan_payment_verification_xls
from hct_mis_api.apps.payment.utils import calculate_counts, from_received_to_status
from hct_mis_api.apps.payment.xlsx.XlsxVerificationImportService import (
    XlsxVerificationImportService,
)
from hct_mis_api.apps.payment.models import CashPlan
from hct_mis_api.apps.program.schema import CashPlanNode, CashPlanPaymentVerification
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin

logger = logging.getLogger(__name__)


class CreatePaymentVerificationMutation(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        input = CreatePaymentVerificationInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        cash_plan_id = decode_id_string(input.get("cash_plan_id"))
        cash_plan = get_object_or_404(CashPlan, id=cash_plan_id)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_CREATE, cash_plan.business_area)

        cash_plan_verification = VerificationPlanCrudServices.create(cash_plan, input)

        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            None,
            cash_plan_verification,
        )
        cash_plan.refresh_from_db()
        return cls(cash_plan=cash_plan)


class EditPaymentVerificationMutation(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        input = EditCashPlanPaymentVerificationInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        cash_plan_verification_id = decode_id_string(input.get("cash_plan_payment_verification_id"))
        cash_plan_verification = get_object_or_404(CashPlanPaymentVerification, id=cash_plan_verification_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), cash_plan_verification)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_UPDATE, cash_plan_verification.business_area)

        old_cash_plan_verification = copy_model_object(cash_plan_verification)
        cash_plan_verification.verification_channel = input.get("verification_channel")
        cash_plan_verification.payment_record_verifications.all().delete()

        cash_plan_verification = VerificationPlanCrudServices.update(cash_plan_verification, input)

        cash_plan_verification.cash_plan.refresh_from_db()
        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_cash_plan_verification,
            cash_plan_verification,
        )
        return cls(cash_plan=cash_plan_verification.cash_plan)


class ActivateCashPlanVerificationMutation(PermissionMutation, ValidationErrorMutationMixin):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def processed_mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        cash_plan_verification_id = decode_id_string(cash_plan_verification_id)
        cash_plan_verification = get_object_or_404(CashPlanPaymentVerification, id=cash_plan_verification_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), cash_plan_verification)

        old_cash_plan_verification = copy_model_object(cash_plan_verification)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_ACTIVATE, cash_plan_verification.business_area)

        cash_plan_verification = VerificationPlanStatusChangeServices(cash_plan_verification).activate()

        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_cash_plan_verification,
            cash_plan_verification,
        )
        return ActivateCashPlanVerificationMutation(cash_plan=cash_plan_verification.cash_plan)


class FinishCashPlanVerificationMutation(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        id = decode_id_string(cash_plan_verification_id)
        cashplan_payment_verification = get_object_or_404(CashPlanPaymentVerification, id=id)
        check_concurrency_version_in_mutation(kwargs.get("version"), cashplan_payment_verification)
        old_cashplan_payment_verification = copy_model_object(cashplan_payment_verification)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_FINISH, cashplan_payment_verification.business_area)

        if cashplan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            logger.error("You can finish only ACTIVE verification")
            raise GraphQLError("You can finish only ACTIVE verification")
        VerificationPlanStatusChangeServices(cashplan_payment_verification).finish()
        cashplan_payment_verification.refresh_from_db()
        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_cashplan_payment_verification,
            cashplan_payment_verification,
        )
        return FinishCashPlanVerificationMutation(cash_plan=cashplan_payment_verification.cash_plan)


class DiscardCashPlanVerificationMutation(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        cash_plan_verification_id = decode_id_string(cash_plan_verification_id)
        cash_plan_verification = get_object_or_404(CashPlanPaymentVerification, id=cash_plan_verification_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), cash_plan_verification)

        old_cash_plan_verification = copy_model_object(cash_plan_verification)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_DISCARD, cash_plan_verification.business_area)

        cash_plan_verification = VerificationPlanStatusChangeServices(cash_plan_verification).discard()

        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_cash_plan_verification,
            cash_plan_verification,
        )
        return cls(cash_plan=cash_plan_verification.cash_plan)


class InvalidCashPlanVerificationMutation(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        cash_plan_verification_id = decode_id_string(cash_plan_verification_id)
        cash_plan_verification = get_object_or_404(CashPlanPaymentVerification, id=cash_plan_verification_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), cash_plan_verification)

        old_cash_plan_verification = copy_model_object(cash_plan_verification)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_INVALID, cash_plan_verification.business_area)

        cash_plan_verification = VerificationPlanStatusChangeServices(cash_plan_verification).mark_invalid()

        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_cash_plan_verification,
            cash_plan_verification,
        )
        return cls(cash_plan=cash_plan_verification.cash_plan)


class DeleteCashPlanVerificationMutation(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        cash_plan_verification_id = decode_id_string(cash_plan_verification_id)
        cash_plan_verification = get_object_or_404(CashPlanPaymentVerification, id=cash_plan_verification_id)
        cash_plan = cash_plan_verification.cash_plan

        check_concurrency_version_in_mutation(kwargs.get("version"), cash_plan_verification)

        old_cash_plan_verification = copy_model_object(cash_plan_verification)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_DELETE, cash_plan_verification.business_area)

        VerificationPlanCrudServices.delete(cash_plan_verification)

        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_cash_plan_verification,
            None,
        )
        return cls(cash_plan=cash_plan)


class UpdatePaymentVerificationStatusAndReceivedAmount(graphene.Mutation):
    # TODO I don't think this is being used now, add permission if in use

    payment_verification = graphene.Field(PaymentVerificationNode)

    class Arguments:
        payment_verification_id = graphene.ID(required=True)
        received_amount = graphene.Decimal(required=True)
        status = graphene.Argument(
            graphene.Enum(
                "PaymentVerificationStatusForUpdate",
                [(x[0], x[0]) for x in PaymentVerification.STATUS_CHOICES],
            )
        )
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root,
        info,
        payment_verification_id,
        received_amount,
        status,
        **kwargs,
    ):
        payment_verification = get_object_or_404(PaymentVerification, id=decode_id_string(payment_verification_id))
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification)
        old_payment_verification = copy_model_object(payment_verification)
        if (
            payment_verification.cash_plan_payment_verification.verification_channel
            != CashPlanPaymentVerification.VERIFICATION_CHANNEL_MANUAL
        ):
            logger.error("You can only update status of payment verification for MANUAL verification method")
            raise GraphQLError("You can only update status of payment verification for MANUAL verification method")
        if payment_verification.cash_plan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            logger.error(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
            raise GraphQLError(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
        delivered_amount = payment_verification.payment_record.delivered_quantity
        if status == PaymentVerification.STATUS_PENDING and received_amount is not None:
            logger.error(
                f"Wrong status {PaymentVerification.STATUS_PENDING} when received_amount ({received_amount}) is not empty",
            )
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_PENDING} when received_amount ({received_amount}) is not empty",
            )
        elif (
            status == PaymentVerification.STATUS_NOT_RECEIVED
            and received_amount is not None
            and received_amount != Decimal(0)
        ):
            logger.error(
                f"Wrong status {PaymentVerification.STATUS_NOT_RECEIVED} when received_amount ({received_amount}) is not 0 or empty",
            )
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_NOT_RECEIVED} when received_amount ({received_amount}) is not 0 or empty",
            )
        elif status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES and (
            received_amount is None or received_amount == Decimal(0)
        ):
            logger.error(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED_WITH_ISSUES} when received_amount ({received_amount}) is 0 or empty",
            )
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED_WITH_ISSUES} when received_amount ({received_amount}) is 0 or empty",
            )
        elif status == PaymentVerification.STATUS_RECEIVED and received_amount != delivered_amount:
            received_amount_text = "None" if received_amount is None else received_amount
            logger.error(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED} when received_amount ({received_amount_text}) ≠ delivered_amount ({delivered_amount})"
            )
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED} when received_amount ({received_amount_text}) ≠ delivered_amount ({delivered_amount})"
            )
        payment_verification.status = status
        payment_verification.received_amount = received_amount
        payment_verification.save()
        cashplan_payment_verification = payment_verification.cash_plan_payment_verification
        old_cashplan_payment_verification = copy_model_object(cashplan_payment_verification)
        calculate_counts(cashplan_payment_verification)
        cashplan_payment_verification.save()

        log_create(
            CashPlanPaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_cashplan_payment_verification,
            cashplan_payment_verification,
        )
        log_create(
            PaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_payment_verification,
            payment_verification,
        )
        return UpdatePaymentVerificationStatusAndReceivedAmount(payment_verification)


class UpdatePaymentVerificationReceivedAndReceivedAmount(PermissionMutation):
    payment_verification = graphene.Field(PaymentVerificationNode)

    class Arguments:
        payment_verification_id = graphene.ID(required=True)
        received_amount = graphene.Decimal(required=True)
        received = graphene.Boolean(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root,
        info,
        payment_verification_id,
        received_amount,
        received,
        **kwargs,
    ):
        if math.isnan(received_amount):
            received_amount = None
        payment_verification = get_object_or_404(PaymentVerification, id=decode_id_string(payment_verification_id))
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification)
        old_payment_verification = copy_model_object(payment_verification)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_VERIFY, payment_verification.business_area)
        if (
            payment_verification.cash_plan_payment_verification.verification_channel
            != CashPlanPaymentVerification.VERIFICATION_CHANNEL_MANUAL
        ):
            logger.error("You can only update status of payment verification for MANUAL verification method")
            raise GraphQLError("You can only update status of payment verification for MANUAL verification method")
        if payment_verification.cash_plan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            logger.error(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
            raise GraphQLError(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
        if not payment_verification.is_manually_editable:
            logger.error("You can only edit payment verification in first 10 minutes")
            raise GraphQLError("You can only edit payment verification in first 10 minutes")
        delivered_amount = payment_verification.payment_record.delivered_quantity

        if received is None and received_amount is not None and received_amount == 0:
            logger.error(f"You can't set received_amount {received_amount} and not set received to NO")
            raise GraphQLError(f"You can't set received_amount {received_amount} and not set received to NO")
        if received is None and received_amount is not None:
            logger.error(f"You can't set received_amount {received_amount} and not set received to YES")
            raise GraphQLError(f"You can't set received_amount {received_amount} and not set received to YES")
        elif received_amount == 0 and received:
            logger.error(
                "If received_amount is 0, you should set received to NO",
            )
            raise GraphQLError(
                "If received_amount is 0, you should set received to NO",
            )
        elif received_amount is not None and received_amount != 0 and not received:
            logger.error(f"If received_amount({received_amount}) is not 0, you should set received to YES")
            raise GraphQLError(f"If received_amount({received_amount}) is not 0, you should set received to YES")

        payment_verification.status = from_received_to_status(received, received_amount, delivered_amount)
        payment_verification.status_date = timezone.now()
        payment_verification.received_amount = received_amount
        payment_verification.save()
        cashplan_payment_verification = payment_verification.cash_plan_payment_verification
        calculate_counts(cashplan_payment_verification)
        cashplan_payment_verification.save()
        log_create(
            PaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_payment_verification,
            payment_verification,
        )
        return UpdatePaymentVerificationStatusAndReceivedAmount(payment_verification)


class XlsxErrorNode(graphene.ObjectType):
    sheet = graphene.String()
    coordinates = graphene.String()
    message = graphene.String()

    def resolve_sheet(parent, info):
        return parent[0]

    def resolve_coordinates(parent, info):
        return parent[1]

    def resolve_message(parent, info):
        return parent[2]


class ExportXlsxCashPlanVerification(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, cash_plan_verification_id):
        pk = decode_id_string(cash_plan_verification_id)
        cashplan_payment_verification = get_object_or_404(CashPlanPaymentVerification, id=pk)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_EXPORT, cashplan_payment_verification.business_area)

        if cashplan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            logger.error("You can only export verification for active CashPlan verification")
            raise GraphQLError("You can export verification for active CashPlan verification")
        if cashplan_payment_verification.verification_channel != CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX:
            logger.error("You can only export verification when XLSX channel is selected")
            raise GraphQLError("You can export verification when XLSX channel is selected")
        if cashplan_payment_verification.xlsx_file_exporting:
            logger.error("Exporting xlsx file is already started. Please wait")
            raise GraphQLError("Exporting xlsx file is already started. Please wait")
        if cashplan_payment_verification.has_xlsx_cash_plan_payment_verification_file:
            logger.error("Xlsx file is already created")
            raise GraphQLError("Xlsx file is already created")

        cashplan_payment_verification.xlsx_file_exporting = True
        cashplan_payment_verification.save()
        create_cash_plan_payment_verification_xls.delay(pk, info.context.user.pk)
        return cls(cash_plan=cashplan_payment_verification.cash_plan)


class ImportXlsxCashPlanVerification(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)
    errors = graphene.List(XlsxErrorNode)

    class Arguments:
        file = Upload(required=True)
        cash_plan_verification_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, file, cash_plan_verification_id):
        id = decode_id_string(cash_plan_verification_id)
        cashplan_payment_verification = get_object_or_404(CashPlanPaymentVerification, id=id)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_IMPORT, cashplan_payment_verification.business_area)

        if cashplan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            logger.error("You can only import verification for active CashPlan verification")
            raise GraphQLError("You can only import verification for active CashPlan verification")
        if cashplan_payment_verification.verification_channel != CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX:
            logger.error("You can only import verification when XLSX channel is selected")
            raise GraphQLError("You can only import verification when XLSX channel is selected")
        import_service = XlsxVerificationImportService(cashplan_payment_verification, file)
        import_service.open_workbook()
        import_service.validate()
        if len(import_service.errors):
            return ImportXlsxCashPlanVerification(None, import_service.errors)
        import_service.import_verifications()
        calculate_counts(cashplan_payment_verification)
        cashplan_payment_verification.xlsx_file_imported = True
        cashplan_payment_verification.save()
        return ImportXlsxCashPlanVerification(cashplan_payment_verification.cash_plan, import_service.errors)


class CreateFinancialServiceProviderMutation(PermissionMutation):
    financial_service_provider = graphene.Field(FinancialServiceProviderNode)

    class Arguments:
        business_area_slug = graphene.String(required=True)
        inputs = CreateFinancialServiceProviderInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, business_area_slug, inputs):
        cls.has_permission(info, Permissions.FINANCIAL_SERVICE_PROVIDER_CREATE, business_area_slug)

        fsp = FSPService.create(inputs, info.context.user)
        # Schedule task to generate downloadable report
        fsp_generate_xlsx_report_task.delay(fsp.id)

        return cls(financial_service_provider=fsp)


class EditFinancialServiceProviderMutation(PermissionMutation):
    financial_service_provider = graphene.Field(FinancialServiceProviderNode)

    class Arguments:
        business_area_slug = graphene.String(required=True)
        financial_service_provider_id = graphene.ID(required=True)
        inputs = CreateFinancialServiceProviderInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, business_area_slug, financial_service_provider_id, inputs):
        cls.has_permission(info, Permissions.FINANCIAL_SERVICE_PROVIDER_UPDATE, business_area_slug)

        fsp_id = decode_id_string(financial_service_provider_id)
        fsp = FSPService.update(fsp_id, inputs)
        fsp_generate_xlsx_report_task.delay(fsp_id)

        return cls(financial_service_provider=fsp)


class ActionPaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = ActionPaymentPlanInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        payment_plan_id = decode_id_string(input.get("payment_plan_id"))
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        old_payment_plan = copy_model_object(payment_plan)

        # TODO: maybe will update perms here?
        cls.has_permission(info, Permissions.PAYMENT_MODULE_VIEW_DETAILS, payment_plan.business_area)

        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data=input, user=info.context.user
        )

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return cls(payment_plan=payment_plan)


class CreatePaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = CreatePaymentPlanInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        cls.has_permission(info, Permissions.PAYMENT_MODULE_CREATE, input.get("business_area_slug"))

        payment_plan = PaymentPlanService().create(input_data=input, user=info.context.user)

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            new_object=payment_plan,
        )
        return cls(payment_plan=payment_plan)


class UpdatePaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = UpdatePaymentPlanInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        payment_plan_id = decode_id_string(input.get("payment_plan_id"))
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        old_payment_plan = copy_model_object(payment_plan)

        cls.has_permission(info, Permissions.PAYMENT_MODULE_CREATE, payment_plan.business_area)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).update(input_data=input)

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

        return cls(payment_plan=payment_plan)


class DeletePaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        payment_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, payment_plan_id, **kwargs):
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        old_payment_plan = copy_model_object(payment_plan)

        cls.has_permission(info, Permissions.PAYMENT_MODULE_CREATE, payment_plan.business_area)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).delete()

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

        return cls(payment_plan=payment_plan)


class ChooseDeliveryMechanismsForPaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    delivery_mechanisms = graphene.List(graphene.String, required=True)


class ExportXLSXPaymentPlanPaymentListMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        payment_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, payment_plan_id, **kwargs):
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))
        cls.has_permission(info, Permissions.PAYMENT_MODULE_VIEW_LIST, payment_plan.business_area)

        if payment_plan.status != PaymentPlan.Status.LOCKED:
            logger.error("You can only export Payment List for LOCKED Payment Plan")
            raise GraphQLError("You can only export Payment List for LOCKED Payment Plan")

        old_payment_plan = copy_model_object(payment_plan)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).export_xlsx(user=info.context.user)

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

        return cls(payment_plan=payment_plan)


class ChooseDeliveryMechanismsForPaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = ChooseDeliveryMechanismsForPaymentPlanInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(input.get("payment_plan_id")))
        cls.has_permission(info, Permissions.PAYMENT_MODULE_CREATE, payment_plan.business_area)
        if payment_plan.status != PaymentPlan.Status.LOCKED:
            raise GraphQLError("Payment plan must be locked to choose delivery mechanisms")
        delivery_mechanisms_in_order = input.get("delivery_mechanisms")
        if len(list(set(delivery_mechanisms_in_order))) != len(list(delivery_mechanisms_in_order)):
            raise GraphQLError("Delivery mechanisms must be unique")

        collectors_in_target_population = payment_plan.target_population.households.filter(
            individuals_and_roles__role=ROLE_PRIMARY,
        ).values_list("individuals_and_roles__individual", flat=True)

        collectors_that_can_be_paid = PaymentChannel.objects.filter(
            individual__in=collectors_in_target_population,
            delivery_mechanism__in=delivery_mechanisms_in_order,
        ).values_list("individual", flat=True)

        # TODO: use exclude
        collectors_that_cant_be_paid = [
            c for c in collectors_in_target_population if c not in collectors_that_can_be_paid
        ]

        # if collectors_that_cant_be_paid.exists():
        if collectors_that_cant_be_paid:
            raise GraphQLError(
                "Selected delivery mechanisms are not sufficient to serve all beneficiaries. "
                # "Please add TODO to move to next step."
            )

        current_time = timezone.now()
        for index, delivery_mechanism in enumerate(delivery_mechanisms_in_order):
            DeliveryMechanismPerPaymentPlan.objects.update_or_create(
                payment_plan=payment_plan,
                delivery_mechanism=delivery_mechanism,
                sent_date=current_time,
                delivery_mechanism_order=index + 1,
                created_by=info.context.user,
            )
        return cls(payment_plan=payment_plan)


class FSPToDeliveryMechanismMappingInput(graphene.InputObjectType):
    fsp_id = graphene.ID(required=True)
    delivery_mechanism = graphene.String(required=True)


class AssignFspToDeliveryMechanismInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    mappings = graphene.List(FSPToDeliveryMechanismMappingInput, required=True)


class AssignFspToDeliveryMechanismMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = AssignFspToDeliveryMechanismInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(input.get("payment_plan_id")))
        cls.has_permission(info, Permissions.PAYMENT_MODULE_CREATE, payment_plan.business_area)
        if payment_plan.status != PaymentPlan.Status.LOCKED:
            raise GraphQLError("Payment plan must be locked to assign FSP to delivery mechanism")

        mappings = [
            {
                "fsp": get_object_or_404(FinancialServiceProvider, id=decode_id_string(mapping.get("fsp_id"))),
                "delivery_mechanism_per_payment_plan": get_object_or_404(
                    DeliveryMechanismPerPaymentPlan,
                    payment_plan=payment_plan,
                    delivery_mechanism=mapping.get("delivery_mechanism"),
                ),
            }
            for mapping in input.get("mappings")
        ]

        for mapping in mappings:
            delivery_mechanism_per_payment_plan = mapping.get("delivery_mechanism_per_payment_plan")
            fsp = mapping.get("fsp")
            if delivery_mechanism_per_payment_plan.delivery_mechanism not in fsp.delivery_mechanisms:
                raise GraphQLError(
                    f"Delivery mechanism '{delivery_mechanism_per_payment_plan.delivery_mechanism}' is not supported "
                    f"by FSP '{fsp.name}'"
                )
            delivery_mechanism_per_payment_plan.financial_service_provider = fsp
            delivery_mechanism_per_payment_plan.save()

        for delivery_mechanism_per_payment_plan in payment_plan.delivery_mechanisms.all():
            if not delivery_mechanism_per_payment_plan.financial_service_provider:
                raise GraphQLError("Please assign FSP to all delivery mechanisms before moving to next step")

        return cls(payment_plan=payment_plan)


class ImportXLSXPaymentPlanPaymentListMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)
    errors = graphene.List(XlsxErrorNode)

    class Arguments:
        file = Upload(required=True)
        payment_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, file, payment_plan_id):
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        cls.has_permission(info, Permissions.PAYMENT_MODULE_VIEW_LIST, payment_plan.business_area)

        if payment_plan.status != PaymentPlan.Status.LOCKED:
            logger.error("You can only import for LOCKED Payment Plan")
            raise GraphQLError("You can only import for LOCKED Payment Plan")

        import_service = XlsxPaymentPlanImportService(payment_plan, file)
        import_service.open_workbook()
        import_service.validate()
        if import_service.errors:
            return cls(None, import_service.errors)

        payment_plan.status_importing()
        payment_plan.save()

        new_xlsx_file = import_service.remove_old_and_create_new_import_xlsx(info.context.user)
        import_payment_plan_payment_list_from_xlsx.delay(payment_plan.id, new_xlsx_file.id)

        return cls(payment_plan, import_service.errors)


class SetSteficonRuleOnPaymentPlanPaymentListMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Input:
        payment_plan_id = graphene.ID(required=True)
        steficon_rule_id = graphene.ID(required=False)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, payment_plan_id, steficon_rule_id):
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        cls.has_permission(info, Permissions.PAYMENT_MODULE_VIEW_LIST, payment_plan.business_area)

        if payment_plan.status not in (PaymentPlan.Status.LOCKED, PaymentPlan.Status.STEFICON_ERROR):
            logger.error("You can run formula for 'Locked' or 'Rule Engine Errored' statuses of Payment Plan")
            raise GraphQLError("You can run formula for 'Locked' or 'Rule Engine Errored' statuses of Payment Plan")

        old_payment_plan = copy_model_object(payment_plan)

        if steficon_rule_id:
            steficon_rule = get_object_or_404(Rule, id=decode_id_string(steficon_rule_id))
            if not steficon_rule.enabled or steficon_rule.deprecated:
                logger.error("This steficon rule is not enabled or is deprecated.")
                raise GraphQLError("This steficon rule is not enabled or is deprecated.")

            payment_plan.status = PaymentPlan.Status.STEFICON_WAIT
            payment_plan.status_date = timezone.now()
            if steficon_rule.latest.id != payment_plan.steficon_rule_id:
                payment_plan.steficon_rule = steficon_rule.latest

            payment_plan.save()
            payment_plan_apply_steficon.delay(payment_plan.pk)
        else:
            payment_plan.steficon_rule = None
            if payment_plan.status == PaymentPlan.Status.STEFICON_ERROR:
                payment_plan.status_lock()
            payment_plan.save()

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return cls(payment_plan=payment_plan)


class Mutations(graphene.ObjectType):
    create_cash_plan_payment_verification = CreatePaymentVerificationMutation.Field()
    create_financial_service_provider = CreateFinancialServiceProviderMutation.Field()
    edit_financial_service_provider = EditFinancialServiceProviderMutation.Field()
    edit_cash_plan_payment_verification = EditPaymentVerificationMutation.Field()
    export_xlsx_cash_plan_verification = ExportXlsxCashPlanVerification.Field()
    import_xlsx_cash_plan_verification = ImportXlsxCashPlanVerification.Field()
    activate_cash_plan_payment_verification = ActivateCashPlanVerificationMutation.Field()
    finish_cash_plan_payment_verification = FinishCashPlanVerificationMutation.Field()
    discard_cash_plan_payment_verification = DiscardCashPlanVerificationMutation.Field()
    invalid_cash_plan_payment_verification = InvalidCashPlanVerificationMutation.Field()
    delete_cash_plan_payment_verification = DeleteCashPlanVerificationMutation.Field()
    choose_delivery_mechanisms_for_payment_plan = ChooseDeliveryMechanismsForPaymentPlanMutation.Field()
    assign_fsp_to_delivery_mechanism = AssignFspToDeliveryMechanismMutation.Field()
    update_payment_verification_status_and_received_amount = UpdatePaymentVerificationStatusAndReceivedAmount.Field()
    update_payment_verification_received_and_received_amount = (
        UpdatePaymentVerificationReceivedAndReceivedAmount.Field()
    )
    action_payment_plan_mutation = ActionPaymentPlanMutation.Field()
    create_payment_plan = CreatePaymentPlanMutation.Field()
    update_payment_plan = UpdatePaymentPlanMutation.Field()
    delete_payment_plan = DeletePaymentPlanMutation.Field()

    export_xlsx_payment_plan_payment_list = ExportXLSXPaymentPlanPaymentListMutation.Field()
    import_xlsx_payment_plan_payment_list = ImportXLSXPaymentPlanPaymentListMutation.Field()
    set_steficon_rule_on_payment_plan_payment_list = SetSteficonRuleOnPaymentPlanPaymentListMutation.Field()
