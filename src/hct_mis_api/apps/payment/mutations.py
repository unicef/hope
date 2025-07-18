import io
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from zipfile import BadZipFile

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
    decode_id_string_required,
)
from hct_mis_api.apps.core.validators import raise_program_status_is
from hct_mis_api.apps.payment.celery_tasks import (
    create_payment_verification_plan_xlsx,
    export_pdf_payment_plan_summary,
    import_payment_plan_payment_list_from_xlsx,
    payment_plan_apply_engine_rule,
    payment_plan_apply_steficon_hh_selection,
    payment_plan_exclude_beneficiaries,
    payment_plan_full_rebuild,
)
from hct_mis_api.apps.payment.inputs import (
    ActionPaymentPlanInput,
    CreatePaymentPlanInput,
    CreatePaymentVerificationInput,
    EditPaymentVerificationInput,
    OpenPaymentPlanInput,
    UpdatePaymentPlanInput,
)
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentVerification,
    PaymentVerificationPlan,
)
from hct_mis_api.apps.payment.schema import (
    GenericPaymentPlanNode,
    PaymentNode,
    PaymentPlanNode,
    PaymentVerificationNode,
)
from hct_mis_api.apps.payment.services.mark_as_failed import (
    mark_as_failed,
    revert_mark_as_failed,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.payment.services.verification_plan_crud_services import (
    VerificationPlanCrudServices,
)
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.payment.utils import (
    calculate_counts,
    from_received_to_status,
    get_payment_plan_object,
)
from hct_mis_api.apps.payment.xlsx.xlsx_error import XlsxError
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_import_service import (
    XlsxPaymentPlanImportService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_verification_import_service import (
    XlsxVerificationImportService,
)
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.utils.exceptions import log_and_raise
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin
from hct_mis_api.contrib.vision.models import FundsCommitmentItem

if TYPE_CHECKING:  # pragma: no cover
    from uuid import UUID

    from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


class CreateVerificationPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        input = CreatePaymentVerificationInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    @raise_program_status_is(Program.FINISHED)
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "CreateVerificationPlanMutation":
        payment_plan_object: "PaymentPlan" = get_payment_plan_object(input["cash_or_payment_plan_id"])

        check_concurrency_version_in_mutation(kwargs.get("version"), payment_plan_object)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_CREATE, payment_plan_object.business_area)

        verification_plan = VerificationPlanCrudServices.create(payment_plan_object, input)
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(verification_plan.get_program, "pk", None),
            None,
            verification_plan,
        )
        payment_plan_object.save()
        payment_plan_object.refresh_from_db()

        return cls(payment_plan=payment_plan_object)


class EditPaymentVerificationMutation(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        input = EditPaymentVerificationInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "EditPaymentVerificationMutation":
        payment_verification_id = decode_id_string(input.get("payment_verification_plan_id"))
        payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification_plan)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_UPDATE, payment_verification_plan.business_area)

        old_payment_verification_plan = copy_model_object(payment_verification_plan)
        payment_verification_plan.verification_channel = input.get("verification_channel")
        payment_verification_plan.payment_record_verifications.all().delete()

        payment_verification_plan = VerificationPlanCrudServices.update(payment_verification_plan, input)

        payment_verification_plan.payment_plan.refresh_from_db()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return cls(payment_plan=payment_verification_plan.payment_plan)


class ActivatePaymentVerificationPlan(PermissionMutation, ValidationErrorMutationMixin):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        payment_verification_plan_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def processed_mutate(
        cls, root: Any, info: Any, payment_verification_plan_id: Optional[str], **kwargs: Any
    ) -> "ActivatePaymentVerificationPlan":
        payment_verification_plan_id = decode_id_string(payment_verification_plan_id)
        payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification_plan)

        old_payment_verification_plan = copy_model_object(payment_verification_plan)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_ACTIVATE, payment_verification_plan.business_area)

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).activate()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return ActivatePaymentVerificationPlan(payment_plan=payment_verification_plan.payment_plan)


class FinishPaymentVerificationPlan(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        payment_verification_plan_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, payment_verification_plan_id: str, **kwargs: Any
    ) -> "FinishPaymentVerificationPlan":
        payment_verification_plan_id = decode_id_string_required(payment_verification_plan_id)
        payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification_plan)
        old_payment_verification_plan = copy_model_object(payment_verification_plan)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_FINISH, payment_verification_plan.business_area)

        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            log_and_raise("You can finish only ACTIVE verification")
        VerificationPlanStatusChangeServices(payment_verification_plan).finish()
        payment_verification_plan.refresh_from_db()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return FinishPaymentVerificationPlan(payment_plan=payment_verification_plan.payment_plan)


class DiscardPaymentVerificationPlan(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        payment_verification_plan_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, payment_verification_plan_id: Optional[str], **kwargs: Any
    ) -> "DiscardPaymentVerificationPlan":
        payment_verification_plan_id = decode_id_string(payment_verification_plan_id)
        payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification_plan)

        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_DISCARD, payment_verification_plan.business_area)

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).discard()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return cls(payment_plan=payment_verification_plan.payment_plan)


class InvalidPaymentVerificationPlan(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        payment_verification_plan_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, payment_verification_plan_id: Optional[str], **kwargs: Any
    ) -> "InvalidPaymentVerificationPlan":
        payment_verification_plan_id = decode_id_string(payment_verification_plan_id)
        payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification_plan)

        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_INVALID, payment_verification_plan.business_area)

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).mark_invalid()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return cls(payment_plan=payment_verification_plan.payment_plan)


class DeletePaymentVerificationPlan(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        payment_verification_plan_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, payment_verification_plan_id: Optional[str], **kwargs: Any
    ) -> "DeletePaymentVerificationPlan":
        payment_verification_plan_id = decode_id_string(payment_verification_plan_id)
        payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)
        payment_plan = payment_verification_plan.payment_plan
        program_id = getattr(payment_verification_plan.get_program, "pk", None)

        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification_plan)

        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_DELETE, payment_verification_plan.business_area)

        VerificationPlanCrudServices.delete(payment_verification_plan)
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            program_id,
            old_payment_verification_plan,
            None,
        )
        return cls(payment_plan=payment_plan)


class UpdatePaymentVerificationStatusAndReceivedAmount(PermissionMutation):
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
        root: Any,
        info: Any,
        payment_verification_id: Optional[str],
        received_amount: Optional[int],
        status: str,
        **kwargs: Any,
    ) -> "UpdatePaymentVerificationStatusAndReceivedAmount":
        payment_verification = get_object_or_404(PaymentVerification, id=decode_id_string(payment_verification_id))
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification)
        old_payment_verification = copy_model_object(payment_verification)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_VERIFY, payment_verification.business_area)
        if (
            payment_verification.payment_verification_plan.verification_channel
            != PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
        ):
            log_and_raise("You can only update status of payment verification for MANUAL verification method")
        if payment_verification.payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            logger.warning(
                f"You can only update status of payment verification for {PaymentVerificationPlan.STATUS_ACTIVE} cash plan verification"
            )
            raise GraphQLError(
                f"You can only update status of payment verification for {PaymentVerificationPlan.STATUS_ACTIVE} cash plan verification"
            )
        delivered_amount = payment_verification.payment.delivered_quantity
        if status == PaymentVerification.STATUS_PENDING and received_amount is not None:  # pragma: no cover
            logger.warning(
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
            logger.warning(
                f"Wrong status {PaymentVerification.STATUS_NOT_RECEIVED} when received_amount ({received_amount}) is not 0 or empty",
            )
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_NOT_RECEIVED} when received_amount ({received_amount}) is not 0 or empty",
            )
        elif status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES and (
            received_amount is None or received_amount == Decimal(0)
        ):
            logger.warning(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED_WITH_ISSUES} when received_amount ({received_amount}) is 0 or empty",
            )
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED_WITH_ISSUES} when received_amount ({received_amount}) is 0 or empty",
            )
        elif status == PaymentVerification.STATUS_RECEIVED and received_amount != delivered_amount:
            received_amount_text = "None" if received_amount is None else received_amount
            logger.warning(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED} when received_amount ({received_amount_text}) ≠ delivered_amount ({delivered_amount})"
            )
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED} when received_amount ({received_amount_text}) ≠ delivered_amount ({delivered_amount})"
            )
        payment_verification.status = status
        payment_verification.received_amount = received_amount
        payment_verification.save()
        payment_verification_plan = payment_verification.payment_verification_plan
        old_payment_verification_plan = copy_model_object(payment_verification_plan)
        calculate_counts(payment_verification_plan)
        payment_verification_plan.save()
        program_id = getattr(payment_verification_plan.get_program, "pk", None)
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            program_id,
            old_payment_verification_plan,
            payment_verification_plan,
        )
        log_create(
            PaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            program_id,
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
        root: Any,
        info: Any,
        payment_verification_id: str,
        received_amount: Decimal,
        received: bool,
        **kwargs: Any,
    ) -> "UpdatePaymentVerificationReceivedAndReceivedAmount":
        payment_verification = get_object_or_404(PaymentVerification, id=decode_id_string(payment_verification_id))
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification)
        old_payment_verification = copy_model_object(payment_verification)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_VERIFY, payment_verification.business_area)
        if (
            payment_verification.payment_verification_plan.verification_channel
            != PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
        ):
            log_and_raise("You can only update status of payment verification for MANUAL verification method")
        if payment_verification.payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            logger.warning(
                f"You can only update status of payment verification for {PaymentVerificationPlan.STATUS_ACTIVE} cash plan verification"
            )
            raise GraphQLError(
                f"You can only update status of payment verification for {PaymentVerificationPlan.STATUS_ACTIVE} cash plan verification"
            )
        if not payment_verification.is_manually_editable:
            log_and_raise("You can only edit payment verification in first 10 minutes")
        delivered_amount = payment_verification.payment.delivered_quantity

        if received is None and received_amount is not None and received_amount == 0:
            log_and_raise("You can't set received_amount {received_amount} and not set received to NO")
        if received is None and received_amount is not None:
            log_and_raise("You can't set received_amount {received_amount} and not set received to YES")
        elif received_amount == 0 and received:
            log_and_raise("If 'Amount Received' equals to 0, please set status as 'Not Received'")
        elif received_amount is not None and received_amount != 0 and not received:
            log_and_raise(f"If received_amount({received_amount}) is not 0, you should set received to YES")

        payment_verification.status = from_received_to_status(received, received_amount, delivered_amount)
        payment_verification.status_date = timezone.now()
        payment_verification.received_amount = received_amount
        payment_verification.save()
        payment_verification_plan = payment_verification.payment_verification_plan
        calculate_counts(payment_verification_plan)
        payment_verification_plan.save()
        log_create(
            PaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_payment_verification,
            payment_verification,
        )
        return UpdatePaymentVerificationReceivedAndReceivedAmount(payment_verification)


class XlsxErrorNode(graphene.ObjectType):
    sheet = graphene.String()
    coordinates = graphene.String()
    message = graphene.String()

    @staticmethod
    def resolve_sheet(parent: XlsxError, info: Any) -> str:
        return parent.sheet

    @staticmethod
    def resolve_coordinates(parent: XlsxError, info: Any) -> Optional[str]:
        return parent.coordinates

    @staticmethod
    def resolve_message(parent: XlsxError, info: Any) -> str:
        return parent.message


class ExportXlsxPaymentVerificationPlanFile(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)

    class Arguments:
        payment_verification_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    def mutate(cls, root: Any, info: Any, payment_verification_plan_id: str) -> "ExportXlsxPaymentVerificationPlanFile":
        payment_verification_plan_id = decode_id_string_required(payment_verification_plan_id)
        payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_EXPORT, payment_verification_plan.business_area)

        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            log_and_raise("You can only export verification for active CashPlan verification")
        if payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
            log_and_raise("You can only export verification when XLSX channel is selected")
        if payment_verification_plan.xlsx_file_exporting:
            log_and_raise("Exporting xlsx file is already started. Please wait")
        if payment_verification_plan.has_xlsx_payment_verification_plan_file:
            log_and_raise("Xlsx file is already created")

        payment_verification_plan.xlsx_file_exporting = True
        payment_verification_plan.save()
        create_payment_verification_plan_xlsx.delay(payment_verification_plan_id, info.context.user.pk)
        return cls(payment_plan=payment_verification_plan.payment_plan)


class ImportXlsxPaymentVerificationPlanFile(PermissionMutation):
    payment_plan = graphene.Field(GenericPaymentPlanNode)
    errors = graphene.List(XlsxErrorNode)

    class Arguments:
        file = Upload(required=True)
        payment_verification_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    def mutate(
        cls, root: Any, info: Any, file: io.BytesIO, payment_verification_plan_id: str
    ) -> "ImportXlsxPaymentVerificationPlanFile":
        payment_verification_plan = get_object_or_404(
            PaymentVerificationPlan, id=decode_id_string(payment_verification_plan_id)
        )

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_IMPORT, payment_verification_plan.business_area)

        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            log_and_raise("You can only import verification for active CashPlan verification")
        if payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
            log_and_raise("You can only import verification when XLSX channel is selected")
        import_service = XlsxVerificationImportService(payment_verification_plan, file)
        import_service.open_workbook()
        import_service.validate()
        if len(import_service.errors):
            return ImportXlsxPaymentVerificationPlanFile(None, import_service.errors)
        import_service.import_verifications()
        calculate_counts(payment_verification_plan)
        payment_verification_plan.xlsx_file_imported = True
        payment_verification_plan.save()
        return ImportXlsxPaymentVerificationPlanFile(payment_verification_plan.payment_plan, import_service.errors)


class MarkPaymentAsFailedMutation(PermissionMutation):
    payment = graphene.Field(PaymentNode)

    class Arguments:
        payment_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root: Any,
        info: Any,
        payment_id: str,
        **kwargs: Any,
    ) -> "MarkPaymentAsFailedMutation":
        payment = get_object_or_404(Payment, id=decode_id_string(payment_id))
        cls.has_permission(info, Permissions.PM_MARK_PAYMENT_AS_FAILED, payment.business_area)
        mark_as_failed(payment)
        return cls(payment)


class RevertMarkPaymentAsFailedMutation(PermissionMutation):
    payment = graphene.Field(PaymentNode)

    class Arguments:
        payment_id = graphene.ID(required=True)
        delivered_quantity = graphene.Decimal(required=True)
        delivery_date = graphene.Date(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root: Any,
        info: Any,
        payment_id: str,
        delivered_quantity: Decimal,
        delivery_date: date,
        **kwargs: Any,
    ) -> "RevertMarkPaymentAsFailedMutation":
        payment = get_object_or_404(Payment, id=decode_id_string(payment_id))
        cls.has_permission(info, Permissions.PM_MARK_PAYMENT_AS_FAILED, payment.business_area)
        delivery_date = datetime.combine(delivery_date, datetime.min.time())
        revert_mark_as_failed(payment, delivered_quantity, delivery_date)
        return cls(payment)


class ActionPaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = ActionPaymentPlanInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "ActionPaymentPlanMutation":
        payment_plan_id = decode_id_string(input.get("payment_plan_id"))
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_plan)

        old_payment_plan = copy_model_object(payment_plan)
        if old_payment_plan.imported_file:
            old_payment_plan.imported_file = copy_model_object(payment_plan.imported_file)
        if old_payment_plan.export_file_entitlement:
            old_payment_plan.export_file_entitlement = copy_model_object(payment_plan.export_file_entitlement)
        if old_payment_plan.export_file_per_fsp:
            old_payment_plan.export_file_per_fsp = copy_model_object(payment_plan.export_file_per_fsp)

        cls.check_permissions(info, payment_plan.business_area, input.get("action", ""), payment_plan.status)

        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data=input, user=info.context.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return cls(payment_plan=payment_plan)

    @classmethod
    def check_permissions(cls, info: Any, business_area: "BusinessArea", action: str, pp_status: str) -> None:
        def _get_reject_permission(status: str) -> Any:
            status_to_perm_map = {
                PaymentPlan.Status.IN_APPROVAL.name: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                PaymentPlan.Status.IN_AUTHORIZATION.name: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
                PaymentPlan.Status.IN_REVIEW.name: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            }
            return status_to_perm_map.get(status, list(status_to_perm_map.values()))

        action_to_permissions_map = {
            PaymentPlan.Action.TP_LOCK.name: Permissions.TARGETING_LOCK,
            PaymentPlan.Action.TP_UNLOCK.name: Permissions.TARGETING_UNLOCK,
            PaymentPlan.Action.TP_REBUILD.name: Permissions.TARGETING_LOCK,
            PaymentPlan.Action.DRAFT.name: [Permissions.PM_CREATE, Permissions.TARGETING_SEND],
            PaymentPlan.Action.LOCK.name: Permissions.PM_LOCK_AND_UNLOCK,
            PaymentPlan.Action.UNLOCK.name: Permissions.PM_LOCK_AND_UNLOCK,
            PaymentPlan.Action.LOCK_FSP.name: Permissions.PM_LOCK_AND_UNLOCK_FSP,
            PaymentPlan.Action.UNLOCK_FSP.name: Permissions.PM_LOCK_AND_UNLOCK_FSP,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name: Permissions.PM_SEND_FOR_APPROVAL,
            PaymentPlan.Action.APPROVE.name: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            PaymentPlan.Action.AUTHORIZE.name: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            PaymentPlan.Action.REVIEW.name: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            PaymentPlan.Action.REJECT.name: _get_reject_permission(pp_status),
            PaymentPlan.Action.FINISH.name: [],
            PaymentPlan.Action.SEND_TO_PAYMENT_GATEWAY.name: [Permissions.PM_SEND_TO_PAYMENT_GATEWAY],
            PaymentPlan.Action.SEND_XLSX_PASSWORD.name: [Permissions.PM_SEND_XLSX_PASSWORD],
        }
        cls.has_permission(info, action_to_permissions_map[action], business_area)


class CreatePaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = CreatePaymentPlanInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "CreatePaymentPlanMutation":
        business_area_slug = info.context.headers.get("Business-Area")
        cls.has_permission(info, Permissions.PM_CREATE, business_area_slug)

        payment_plan = PaymentPlanService.create(
            input_data=input, user=info.context.user, business_area_slug=business_area_slug
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program.pk,
            new_object=payment_plan,
        )
        return cls(payment_plan=payment_plan)


class OpenPaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = OpenPaymentPlanInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "OpenPaymentPlanMutation":
        business_area_slug = info.context.headers.get("Business-Area")
        cls.has_permission(info, Permissions.PM_CREATE, business_area_slug)
        payment_plan_id = decode_id_string(input.get("payment_plan_id"))
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_plan)
        old_payment_plan = copy_model_object(payment_plan)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).open(input_data=input)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program_cycle.program,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

        return cls(payment_plan=payment_plan)


class UpdatePaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = UpdatePaymentPlanInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "UpdatePaymentPlanMutation":
        payment_plan_id = decode_id_string(input.get("payment_plan_id"))
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_plan)
        old_payment_plan = copy_model_object(payment_plan)

        cls.has_permission(info, [Permissions.PM_CREATE, Permissions.TARGETING_UPDATE], payment_plan.business_area)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).update(input_data=input)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program.pk,
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
    def mutate(cls, root: Any, info: Any, payment_plan_id: str, **kwargs: Any) -> "DeletePaymentPlanMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        old_payment_plan = copy_model_object(payment_plan)

        cls.has_permission(info, Permissions.PM_CREATE, payment_plan.business_area)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).delete()
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

        return cls(payment_plan=payment_plan)


class ExportXLSXPaymentPlanPaymentListMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        payment_plan_id = graphene.ID(required=True)
        fsp_xlsx_template_id = graphene.ID(description="Using for MTCN/Auth Code export")

    @classmethod
    def export_action(
        cls, payment_plan: PaymentPlan, user_id: "UUID", fsp_xlsx_template_id: Optional[str] = None
    ) -> PaymentPlan:
        if payment_plan.status not in [PaymentPlan.Status.LOCKED]:
            msg = "You can only export Payment List for LOCKED Payment Plan"
            raise GraphQLError(msg)

        return PaymentPlanService(payment_plan=payment_plan).export_xlsx(user_id=user_id)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, payment_plan_id: str, fsp_xlsx_template_id: Optional[str] = None, **kwargs: Any
    ) -> "ExportXLSXPaymentPlanPaymentListMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))
        fsp_xlsx_template_id_str: Optional[str] = decode_id_string(fsp_xlsx_template_id)
        cls.has_permission(info, Permissions.PM_VIEW_LIST, payment_plan.business_area)
        if fsp_xlsx_template_id:
            cls.has_permission(info, Permissions.PM_DOWNLOAD_FSP_AUTH_CODE, payment_plan.business_area)

        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = cls.export_action(payment_plan, info.context.user.pk, fsp_xlsx_template_id_str)

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

        return cls(payment_plan=payment_plan)


class ExportXLSXPaymentPlanPaymentListPerFSPMutation(ExportXLSXPaymentPlanPaymentListMutation):
    @classmethod
    def export_action(
        cls, payment_plan: PaymentPlan, user_id: "UUID", fsp_xlsx_template_id: Optional[str] = None
    ) -> PaymentPlan:
        if payment_plan.status not in [PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]:
            msg = "Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans."
            raise GraphQLError(msg)

        if not payment_plan.eligible_payments:
            msg = "Export failed: The Payment List is empty."
            raise GraphQLError(msg)

        if fsp_xlsx_template_id and payment_plan.export_file_per_fsp is not None:
            msg = "Export failed: Payment Plan already has created exported file."
            raise GraphQLError(msg)

        if fsp_xlsx_template_id and not payment_plan.can_create_xlsx_with_fsp_auth_code:
            msg = (
                "Export failed: There could be not Pending Payments and FSP communication channel should be set to API."
            )
            raise GraphQLError(msg)

        return PaymentPlanService(payment_plan=payment_plan).export_xlsx_per_fsp(user_id, fsp_xlsx_template_id)


class ImportXLSXPaymentPlanPaymentListMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)
    errors = graphene.List(XlsxErrorNode)

    class Arguments:
        file = Upload(required=True)
        payment_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, file: io.BytesIO, payment_plan_id: str
    ) -> "ImportXLSXPaymentPlanPaymentListMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        cls.has_permission(info, Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS, payment_plan.business_area)

        if payment_plan.status != PaymentPlan.Status.LOCKED:
            msg = "You can only import for LOCKED Payment Plan"
            logger.warning(msg)
            raise GraphQLError(msg)

        if payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS:
            msg = "Import in progress"
            logger.warning(msg)
            raise GraphQLError(msg)

        with transaction.atomic():
            import_service = XlsxPaymentPlanImportService(payment_plan, file)
            import_service.open_workbook()
            import_service.validate()
            if import_service.errors:
                return cls(None, import_service.errors)

            old_payment_plan = copy_model_object(payment_plan)
            if old_payment_plan.imported_file:
                old_payment_plan.imported_file = copy_model_object(payment_plan.imported_file)

            payment_plan.background_action_status_xlsx_importing_entitlements()
            payment_plan.save()

            payment_plan = import_service.create_import_xlsx_file(info.context.user)

            transaction.on_commit(lambda: import_payment_plan_payment_list_from_xlsx.delay(payment_plan.id))
            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=info.context.user,
                programs=payment_plan.program.pk,
                old_object=old_payment_plan,
                new_object=payment_plan,
            )

        return cls(payment_plan, None)


class ImportXLSXPaymentPlanPaymentListPerFSPMutation(PermissionMutation):
    # PaymentPlan Reconciliation
    payment_plan = graphene.Field(PaymentPlanNode)
    errors = graphene.List(XlsxErrorNode)

    class Arguments:
        file = Upload(required=True)
        payment_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, file: io.BytesIO, payment_plan_id: str
    ) -> "ImportXLSXPaymentPlanPaymentListPerFSPMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        cls.has_permission(info, Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION, payment_plan.business_area)

        if payment_plan.status not in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED):
            msg = "You can only import for ACCEPTED or FINISHED Payment Plan"
            raise GraphQLError(msg)

        if (
            payment_plan.financial_service_provider.communication_channel
            != FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX
        ):
            msg = "Only for FSP with Communication Channel XLSX can be imported reconciliation manually."
            raise GraphQLError(msg)

        import_service = XlsxPaymentPlanImportPerFspService(payment_plan, file)
        try:
            import_service.open_workbook()
        except BadZipFile:
            msg = "Wrong file type or password protected .zip file. Upload another file, or remove the password."
            raise GraphQLError(msg)

        import_service.validate()
        if import_service.errors:
            return cls(payment_plan=None, errors=import_service.errors)

        old_payment_plan = copy_model_object(payment_plan)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).import_xlsx_per_fsp(
            user=info.context.user, file=file
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

        return cls(payment_plan=payment_plan, errors=None)


class SetSteficonRuleOnPaymentPlanPaymentListMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Input:
        payment_plan_id = graphene.ID(required=True)
        steficon_rule_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    def mutate(
        cls, root: Any, info: Any, payment_plan_id: str, steficon_rule_id: str, version: int
    ) -> "SetSteficonRuleOnPaymentPlanPaymentListMutation":
        payment_plan_id = decode_id_string_required(payment_plan_id)
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        check_concurrency_version_in_mutation(version, payment_plan)

        if payment_plan.status in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_VULNERABILITY_SCORE:
            cls.has_permission(info, Permissions.TARGETING_UPDATE, payment_plan.business_area)
        if payment_plan.status in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_ENTITLEMENT:
            cls.has_permission(
                info, Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS, payment_plan.business_area
            )

        if payment_plan.status not in PaymentPlan.CAN_RUN_ENGINE_FORMULA:
            raise GraphQLError("You can run formula only for 'Locked', 'Error' or 'Completed' statuses.")

        old_payment_plan = copy_model_object(payment_plan)
        engine_rule = get_object_or_404(Rule, id=decode_id_string(steficon_rule_id))
        if not engine_rule.enabled or engine_rule.deprecated:
            raise GraphQLError("This engine rule is not enabled or is deprecated.")

        # PaymentPlan vulnerability_score
        if payment_plan.status in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_VULNERABILITY_SCORE:
            rule_commit = engine_rule.latest
            if not engine_rule.enabled or engine_rule.deprecated:
                raise GraphQLError("This engine rule is not enabled or is deprecated.")
            payment_plan.steficon_rule_targeting = rule_commit
            payment_plan.status = PaymentPlan.Status.TP_STEFICON_WAIT
            payment_plan.save()
            payment_plan_apply_steficon_hh_selection.delay(str(payment_plan.pk), str(engine_rule.pk))

        # PaymentPlan entitlement
        if payment_plan.status in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_ENTITLEMENT:
            if payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RULE_ENGINE_RUN:
                raise GraphQLError("Rule Engine run in progress")
            payment_plan.background_action_status_steficon_run()
            payment_plan.save()
            payment_plan_apply_engine_rule.delay(str(payment_plan.pk), str(engine_rule.pk))

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=info.context.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return cls(payment_plan=payment_plan)


class ExcludeHouseholdsMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Input:
        payment_plan_id = graphene.ID(required=True)
        excluded_households_ids = graphene.List(graphene.String, required=True)
        exclusion_reason = graphene.String()

    @classmethod
    @is_authenticated
    def mutate(
        cls,
        root: Any,
        info: Any,
        payment_plan_id: str,
        excluded_households_ids: List[str],
        exclusion_reason: Optional[str] = "",
    ) -> "ExcludeHouseholdsMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        cls.has_permission(info, Permissions.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP, payment_plan.business_area)

        if payment_plan.status not in (PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED):
            raise GraphQLError("Beneficiary can be excluded only for 'Open' or 'Locked' status of Payment Plan")

        payment_plan_exclude_beneficiaries.delay(
            decode_id_string(payment_plan_id), excluded_households_ids, exclusion_reason
        )

        payment_plan.background_action_status_excluding_beneficiaries()
        payment_plan.exclude_household_error = ""
        payment_plan.save(update_fields=["background_action_status", "exclude_household_error"])

        payment_plan.refresh_from_db()
        return cls(payment_plan=payment_plan)


class CreateFollowUpPaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        payment_plan_id = graphene.ID(required=True)
        dispersion_start_date = graphene.Date(required=True)
        dispersion_end_date = graphene.Date(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root: Any,
        info: Any,
        payment_plan_id: str,
        dispersion_start_date: date,
        dispersion_end_date: date,
        **kwargs: Any,
    ) -> "CreateFollowUpPaymentPlanMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))
        cls.has_permission(info, Permissions.PM_CREATE, payment_plan.business_area)

        follow_up_pp = PaymentPlanService(payment_plan).create_follow_up(
            info.context.user, dispersion_start_date, dispersion_end_date
        )

        return cls(follow_up_pp)


class ExportPDFPaymentPlanSummaryMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        payment_plan_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root: Any,
        info: Any,
        payment_plan_id: str,
        **kwargs: Any,
    ) -> "ExportPDFPaymentPlanSummaryMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))
        cls.has_permission(info, Permissions.PM_EXPORT_PDF_SUMMARY, payment_plan.business_area)
        export_pdf_payment_plan_summary.delay(payment_plan.pk, info.context.user.pk)

        return cls(payment_plan=payment_plan)


class SplitPaymentPlanMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        payment_plan_id = graphene.ID(required=True)
        split_type = graphene.String(required=True)
        payments_no = graphene.Int(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, payment_plan_id: str, split_type: str, payments_no: Optional[int], **kwargs: Any
    ) -> "SplitPaymentPlanMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))
        cls.has_permission(info, Permissions.PM_SPLIT, payment_plan.business_area)

        splits_sent_to_pg = payment_plan.splits.filter(
            sent_to_payment_gateway=True,
        )
        if splits_sent_to_pg.exists():
            raise GraphQLError("Payment plan is already sent to payment gateway")

        if payment_plan.status != PaymentPlan.Status.ACCEPTED:
            raise GraphQLError("Payment plan must be accepted to make a split")

        if split_type == PaymentPlanSplit.SplitType.BY_RECORDS:
            if not payments_no:
                raise GraphQLError("Payment Number is required for split by records")
            if (payment_plan.eligible_payments.count() // payments_no) > PaymentPlanSplit.MAX_CHUNKS:
                raise GraphQLError(f"Cannot split Payment Plan into more than {PaymentPlanSplit.MAX_CHUNKS} parts")

        with transaction.atomic():
            payment_plan_service = PaymentPlanService(payment_plan=payment_plan)
            payment_plan_service.split(split_type, payments_no)

        return cls(payment_plan=payment_plan)


class CopyTargetingCriteriaMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        payment_plan_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        program_cycle_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, payment_plan_id: str, name: str, program_cycle_id: str, **kwargs: Any
    ) -> "CopyTargetingCriteriaMutation":
        user = info.context.user
        name = name.strip()
        payment_plan_id = decode_id_string_required(payment_plan_id)
        payment_plan = get_object_or_404(PaymentPlan, pk=payment_plan_id)
        program_cycle = get_object_or_404(ProgramCycle, pk=decode_id_string(program_cycle_id))
        program = program_cycle.program

        cls.has_permission(info, Permissions.TARGETING_DUPLICATE, payment_plan.business_area)

        if program_cycle.status == ProgramCycle.FINISHED:
            raise GraphQLError("Not possible to assign Finished Program Cycle to Targeting")

        if PaymentPlan.objects.filter(name=name, program_cycle=program_cycle, is_removed=False).exists():
            raise GraphQLError(
                f"Payment Plan with name: {name} and program cycle: {program_cycle.title} already exists."
            )

        payment_plan_copy = PaymentPlan(
            name=name,
            created_by=user,
            business_area=payment_plan.business_area,
            status=PaymentPlan.Status.TP_OPEN,
            status_date=timezone.now(),
            start_date=program_cycle.start_date,
            end_date=program_cycle.end_date,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
            built_at=timezone.now(),
            male_children_count=payment_plan.male_children_count,
            female_children_count=payment_plan.female_children_count,
            male_adults_count=payment_plan.male_adults_count,
            female_adults_count=payment_plan.female_adults_count,
            total_households_count=payment_plan.total_households_count,
            total_individuals_count=payment_plan.total_individuals_count,
            steficon_rule_targeting=payment_plan.steficon_rule_targeting,
            steficon_targeting_applied_date=payment_plan.steficon_targeting_applied_date,
            program_cycle=program_cycle,
        )
        PaymentPlanService.copy_target_criteria(payment_plan, payment_plan_copy)

        payment_plan_copy.save()
        payment_plan_copy.refresh_from_db()

        transaction.on_commit(lambda: payment_plan_full_rebuild.delay(payment_plan_copy.id))
        log_create(
            PaymentPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            getattr(program, "pk", None),
            None,
            payment_plan_copy,
        )
        return cls(payment_plan=payment_plan_copy)


class AssignFundsCommitmentsMutation(PermissionMutation):
    payment_plan = graphene.Field(PaymentPlanNode)

    class Input:
        payment_plan_id = graphene.ID(required=True)
        fund_commitment_items_ids = graphene.List(graphene.String)

    @classmethod
    @is_authenticated
    def mutate(
        cls,
        root: Any,
        info: Any,
        payment_plan_id: str,
        fund_commitment_items_ids: List[Optional[str]],
    ) -> "AssignFundsCommitmentsMutation":
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))

        cls.has_permission(info, Permissions.PM_ASSIGN_FUNDS_COMMITMENTS, payment_plan.business_area)

        if payment_plan.status != PaymentPlan.Status.IN_REVIEW:
            raise GraphQLError("Payment plan must be in review")

        funds_commitment_items = FundsCommitmentItem.objects.filter(rec_serial_number__in=fund_commitment_items_ids)
        if funds_commitment_items.filter(payment_plan_id__isnull=False).exclude(payment_plan=payment_plan).exists():
            raise GraphQLError("Chosen Funds Commitments are already assigned to different Payment Plan")

        if funds_commitment_items.exclude(office=payment_plan.business_area).exists():
            raise GraphQLError("Chosen Funds Commitments have wrong Business Area")

        FundsCommitmentItem.objects.filter(payment_plan=payment_plan).update(payment_plan=None)
        funds_commitment_items.update(payment_plan=payment_plan)

        payment_plan.refresh_from_db()
        return cls(payment_plan=payment_plan)


class Mutations(graphene.ObjectType):
    # PaymentVerification
    create_payment_verification_plan = CreateVerificationPlanMutation.Field()
    edit_payment_verification_plan = EditPaymentVerificationMutation.Field()

    export_xlsx_payment_verification_plan_file = ExportXlsxPaymentVerificationPlanFile.Field()
    import_xlsx_payment_verification_plan_file = ImportXlsxPaymentVerificationPlanFile.Field()
    activate_payment_verification_plan = ActivatePaymentVerificationPlan.Field()
    finish_payment_verification_plan = FinishPaymentVerificationPlan.Field()
    discard_payment_verification_plan = DiscardPaymentVerificationPlan.Field()
    invalid_payment_verification_plan = InvalidPaymentVerificationPlan.Field()
    delete_payment_verification_plan = DeletePaymentVerificationPlan.Field()
    mark_payment_as_failed = MarkPaymentAsFailedMutation.Field()
    revert_mark_payment_as_failed = RevertMarkPaymentAsFailedMutation.Field()
    update_payment_verification_status_and_received_amount = UpdatePaymentVerificationStatusAndReceivedAmount.Field()
    update_payment_verification_received_and_received_amount = (
        UpdatePaymentVerificationReceivedAndReceivedAmount.Field()
    )

    # Payment Plan
    action_payment_plan_mutation = ActionPaymentPlanMutation.Field()
    create_payment_plan = CreatePaymentPlanMutation.Field()
    open_payment_plan = OpenPaymentPlanMutation.Field()
    create_follow_up_payment_plan = CreateFollowUpPaymentPlanMutation.Field()
    update_payment_plan = UpdatePaymentPlanMutation.Field()
    delete_payment_plan = DeletePaymentPlanMutation.Field()
    split_payment_plan = SplitPaymentPlanMutation.Field()
    exclude_households = ExcludeHouseholdsMutation.Field()
    set_steficon_rule_on_payment_plan_payment_list = SetSteficonRuleOnPaymentPlanPaymentListMutation.Field()
    copy_targeting_criteria = CopyTargetingCriteriaMutation.Field()
    assign_funds_commitments = AssignFundsCommitmentsMutation.Field()

    # Payment Plan XLSX
    export_xlsx_payment_plan_payment_list = ExportXLSXPaymentPlanPaymentListMutation.Field()
    export_xlsx_payment_plan_payment_list_per_fsp = ExportXLSXPaymentPlanPaymentListPerFSPMutation.Field()
    import_xlsx_payment_plan_payment_list = ImportXLSXPaymentPlanPaymentListMutation.Field()
    import_xlsx_payment_plan_payment_list_per_fsp = ImportXLSXPaymentPlanPaymentListPerFSPMutation.Field()

    # Payment Plan PDF
    export_pdf_payment_plan_summary = ExportPDFPaymentPlanSummaryMutation.Field()
