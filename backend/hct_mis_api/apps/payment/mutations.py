import logging
import math
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

import graphene
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

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
    create_cash_plan_payment_verification_xls,
)
from hct_mis_api.apps.payment.inputs import (
    CreatePaymentVerificationInput,
    EditCashPlanPaymentVerificationInput,
)
from hct_mis_api.apps.payment.models import PaymentRecord, PaymentVerification
from hct_mis_api.apps.payment.schema import PaymentRecordNode, PaymentVerificationNode
from hct_mis_api.apps.payment.services.mark_as_failed import mark_as_failed
from hct_mis_api.apps.payment.services.verification_plan_crud_services import (
    VerificationPlanCrudServices,
)
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.payment.utils import calculate_counts, from_received_to_status
from hct_mis_api.apps.payment.xlsx.XlsxVerificationImportService import (
    XlsxVerificationImportService,
)
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.program.schema import CashPlanNode, CashPlanPaymentVerification
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin
from hct_mis_api.apps.utils.exceptions import log_and_raise

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
            log_and_raise("You can finish only ACTIVE verification")
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
            log_and_raise("You can only update status of payment verification for MANUAL verification method")
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
            log_and_raise("You can only update status of payment verification for MANUAL verification method")
        if payment_verification.cash_plan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            logger.error(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
            raise GraphQLError(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
        if not payment_verification.is_manually_editable:
            log_and_raise("You can only edit payment verification in first 10 minutes")
        delivered_amount = payment_verification.payment_record.delivered_quantity

        if received is None and received_amount is not None and received_amount == 0:
            log_and_raise("You can't set received_amount {received_amount} and not set received to NO")
        if received is None and received_amount is not None:
            log_and_raise("You can't set received_amount {received_amount} and not set received to YES")
        elif received_amount == 0 and received:
            logger.error(
                "If received_amount is 0, you should set received to NO",
            )
            raise GraphQLError(
                "If received_amount is 0, you should set received to NO",
            )
        elif received_amount is not None and received_amount != 0 and not received:
            log_and_raise(f"If received_amount({received_amount}) is not 0, you should set received to YES")

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
            log_and_raise("You can only export verification for active CashPlan verification")
        if cashplan_payment_verification.verification_channel != CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX:
            log_and_raise("You can only export verification when XLSX channel is selected")
        if cashplan_payment_verification.xlsx_file_exporting:
            log_and_raise("Exporting xlsx file is already started. Please wait")
        if cashplan_payment_verification.has_xlsx_cash_plan_payment_verification_file:
            log_and_raise("Xlsx file is already created")

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
            log_and_raise("You can only import verification for active CashPlan verification")
        if cashplan_payment_verification.verification_channel != CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX:
            log_and_raise("You can only import verification when XLSX channel is selected")
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


class MarkPaymentRecordAsFailedMutation(PermissionMutation):
    payment_record = graphene.Field(PaymentRecordNode)

    class Arguments:
        payment_record_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root,
        info,
        payment_record_id,
        **kwargs,
    ):
        payment_record = get_object_or_404(PaymentRecord, id=decode_id_string(payment_record_id))

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_MARK_AS_FAILED, payment_record.business_area)

        try:
            mark_as_failed(payment_record)
        except ValidationError as e:
            log_and_raise(e.message, e)

        return MarkPaymentRecordAsFailedMutation(payment_record)


class Mutations(graphene.ObjectType):
    create_cash_plan_payment_verification = CreatePaymentVerificationMutation.Field()
    edit_cash_plan_payment_verification = EditPaymentVerificationMutation.Field()
    export_xlsx_cash_plan_verification = ExportXlsxCashPlanVerification.Field()
    import_xlsx_cash_plan_verification = ImportXlsxCashPlanVerification.Field()
    activate_cash_plan_payment_verification = ActivateCashPlanVerificationMutation.Field()
    finish_cash_plan_payment_verification = FinishCashPlanVerificationMutation.Field()
    discard_cash_plan_payment_verification = DiscardCashPlanVerificationMutation.Field()
    invalid_cash_plan_payment_verification = InvalidCashPlanVerificationMutation.Field()
    delete_cash_plan_payment_verification = DeleteCashPlanVerificationMutation.Field()
    update_payment_verification_status_and_received_amount = UpdatePaymentVerificationStatusAndReceivedAmount.Field()
    mark_payment_record_as_failed = MarkPaymentRecordAsFailedMutation.Field()
    update_payment_verification_received_and_received_amount = (
        UpdatePaymentVerificationReceivedAndReceivedAmount.Field()
    )
