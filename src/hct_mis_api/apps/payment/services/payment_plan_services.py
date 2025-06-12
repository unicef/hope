import datetime
import logging
from functools import partial
from itertools import groupby
from typing import IO, TYPE_CHECKING, Callable, Dict, Optional, Union

from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import OuterRef
from django.shortcuts import get_object_or_404
from django.utils import timezone

from constance import config
from psycopg2._psycopg import IntegrityError

from hct_mis_api.apps.core.currencies import USDC
from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.core.utils import chunks
from hct_mis_api.apps.household.models import (
    ROLE_PRIMARY,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.celery_tasks import (
    create_payment_plan_payment_list_xlsx,
    create_payment_plan_payment_list_xlsx_per_fsp,
    import_payment_plan_payment_list_per_fsp_from_xlsx,
    payment_plan_full_rebuild,
    payment_plan_rebuild_stats,
    prepare_follow_up_payment_plan_task,
    prepare_payment_plan_task,
    send_payment_notification_emails,
    send_payment_plan_payment_list_xlsx_per_fsp_password,
    send_to_payment_gateway,
)
from hct_mis_api.apps.payment.models import (
    Approval,
    ApprovalProcess,
    DeliveryMechanism,
    FinancialServiceProvider,
    Payment,
    PaymentDataCollector,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorRuleFilterBlock,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingIndividualRuleFilterBlock,
)
from hct_mis_api.apps.targeting.services.utils import from_input_to_targeting_criteria
from hct_mis_api.apps.targeting.validators import TargetingCriteriaInputValidator

if TYPE_CHECKING:  # pragma: no cover
    from uuid import UUID

    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser

    from hct_mis_api.apps.account.models import AbstractUser, User


class PaymentPlanService:
    def __init__(self, payment_plan: "PaymentPlan"):
        self.payment_plan = payment_plan

        self.action: Optional[str] = None
        self.user: Optional["User"] = None
        self.input_data: Optional[Dict] = None

    @property
    def actions_map(self) -> Dict:
        return {
            # old TP
            PaymentPlan.Action.TP_LOCK.value: self.tp_lock,
            PaymentPlan.Action.TP_UNLOCK.value: self.tp_unlock,
            PaymentPlan.Action.TP_REBUILD.value: self.tp_rebuild,
            PaymentPlan.Action.DRAFT.value: self.draft,
            # PP
            PaymentPlan.Action.LOCK.value: self.lock,
            PaymentPlan.Action.LOCK_FSP.value: self.lock_fsp,
            PaymentPlan.Action.UNLOCK.value: self.unlock,
            PaymentPlan.Action.UNLOCK_FSP.value: self.unlock_fsp,
            PaymentPlan.Action.SEND_FOR_APPROVAL.value: self.send_for_approval,
            # use the same method for Approve, Authorize, Finance Release and Reject
            PaymentPlan.Action.APPROVE.value: self.acceptance_process,
            PaymentPlan.Action.AUTHORIZE.value: self.acceptance_process,
            PaymentPlan.Action.REVIEW.value: self.acceptance_process,
            PaymentPlan.Action.REJECT.value: self.acceptance_process,
            PaymentPlan.Action.SEND_TO_PAYMENT_GATEWAY.value: self.send_to_payment_gateway,
            PaymentPlan.Action.SEND_XLSX_PASSWORD.value: self.send_xlsx_password,
        }

    def get_required_number_by_approval_type(self, approval_process: ApprovalProcess) -> Optional[int]:
        approval_count_map = {
            Approval.APPROVAL: approval_process.approval_number_required,
            Approval.AUTHORIZATION: approval_process.authorization_number_required,
            Approval.FINANCE_RELEASE: approval_process.finance_release_number_required,
            Approval.REJECT: 1,  # be default only one Reject per Acceptance Process object
        }
        return approval_count_map.get(self.get_approval_type_by_action())

    def get_approval_type_by_action(self) -> str:
        if not self.action:
            raise ValueError("Action cannot be None")

        actions_to_approval_type_map = {
            PaymentPlan.Action.APPROVE.value: Approval.APPROVAL,
            PaymentPlan.Action.AUTHORIZE.value: Approval.AUTHORIZATION,
            PaymentPlan.Action.REVIEW.value: Approval.FINANCE_RELEASE,
            PaymentPlan.Action.REJECT.value: Approval.REJECT,
        }
        return actions_to_approval_type_map[self.action]

    def execute_update_status_action(self, input_data: Dict, user: Union["AbstractUser", "User"]) -> PaymentPlan:
        """Get function from get_action_function and execute it
        return PaymentPlan object
        """
        self.action = input_data.get("action")
        self.input_data = input_data
        self.user = user
        self.validate_action()

        function_action = self.get_action_function()
        payment_plan = function_action()

        return payment_plan

    def validate_action(self) -> None:
        actions = list(self.actions_map.keys())
        if self.action not in actions:
            raise ValidationError(f"Not Implemented Action: {self.action}. List of possible actions: {actions}")

    def get_action_function(self) -> Optional[Callable]:
        return self.actions_map.get(self.action)

    def send_for_approval(self) -> PaymentPlan:
        self.payment_plan.status_send_to_approval()
        self.payment_plan.save()
        # create new ApprovalProcess
        ApprovalProcess.objects.create(
            payment_plan=self.payment_plan,
            sent_for_approval_by=self.user,
            sent_for_approval_date=timezone.now(),
            approval_number_required=self.payment_plan.approval_number_required,
            authorization_number_required=self.payment_plan.authorization_number_required,
            finance_release_number_required=self.payment_plan.finance_release_number_required,
        )
        send_payment_notification_emails.delay(
            self.payment_plan.id,
            PaymentPlan.Action.SEND_FOR_APPROVAL.value,
            self.user.id,
            f"{timezone.now():%-d %B %Y}",
        )
        return self.payment_plan

    def send_to_payment_gateway(self) -> PaymentPlan:
        if self.payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY:
            raise ValidationError("Sending in progress")

        if self.payment_plan.can_send_to_payment_gateway:
            send_to_payment_gateway.delay(self.payment_plan.pk, self.user.pk)
        else:
            raise ValidationError("Already sent to Payment Gateway")

        return self.payment_plan

    def tp_lock(self) -> PaymentPlan:
        self.payment_plan.status_tp_lock()
        self.payment_plan.save(update_fields=("status", "status_date"))

        return self.payment_plan

    def tp_unlock(self) -> PaymentPlan:
        self.payment_plan.status_tp_open()

        self.payment_plan.build_status_pending()
        self.payment_plan.save(update_fields=("build_status", "built_at", "status", "status_date"))
        transaction.on_commit(lambda: payment_plan_rebuild_stats.delay(str(self.payment_plan.id)))

        return self.payment_plan

    def tp_rebuild(self) -> PaymentPlan:
        if self.payment_plan.status not in [PaymentPlan.Status.TP_OPEN, PaymentPlan.Status.TP_LOCKED]:
            raise ValidationError("Can only Rebuild Population for Locked or Open Population status")

        self.payment_plan.build_status_pending()
        self.payment_plan.save(update_fields=("build_status", "built_at"))
        transaction.on_commit(lambda: payment_plan_full_rebuild.delay(str(self.payment_plan.id)))
        return self.payment_plan

    def draft(self) -> PaymentPlan:
        if not self.payment_plan.financial_service_provider:
            raise GraphQLError("Can only promote to Payment Plan if DM/FSP is chosen.")
        self.payment_plan.status_draft()
        self.payment_plan.save(update_fields=("status_date", "status"))
        return self.payment_plan

    def open(self, input_data: Dict) -> PaymentPlan:
        self.payment_plan.status_open()
        dispersion_end_date = input_data["dispersion_end_date"]
        if not dispersion_end_date or dispersion_end_date <= timezone.now().date():
            raise ValidationError(f"Dispersion End Date [{dispersion_end_date}] cannot be a past date")

        self.payment_plan.currency = input_data["currency"]
        self.payment_plan.dispersion_start_date = input_data["dispersion_start_date"]
        self.payment_plan.dispersion_end_date = dispersion_end_date
        self.payment_plan.exchange_rate = self.payment_plan.get_exchange_rate()

        self.payment_plan.save(
            update_fields=(
                "status_date",
                "status",
                "currency",
                "dispersion_start_date",
                "dispersion_end_date",
                "exchange_rate",
            )
        )
        self.payment_plan.program_cycle.set_active()

        # add currency
        Payment.objects.filter(parent=self.payment_plan).update(currency=self.payment_plan.currency)
        self.payment_plan.update_money_fields()

        return self.payment_plan

    def lock(self) -> PaymentPlan:
        if not self.payment_plan.can_be_locked:
            raise ValidationError("At least one valid Payment should exist in order to Lock the Payment Plan")

        self.payment_plan.payment_items.all().filter(payment_plan_hard_conflicted=True).update(conflicted=True)
        self.payment_plan.status_lock()
        self.payment_plan.update_population_count_fields()
        self.payment_plan.update_money_fields()

        self.payment_plan.save()

        return self.payment_plan

    def unlock(self) -> PaymentPlan:
        self.payment_plan.payment_items.all().update(conflicted=False)
        self.payment_plan.status_unlock()
        self.payment_plan.update_population_count_fields()
        self.payment_plan.update_money_fields()
        self.payment_plan.remove_export_files()

        self.payment_plan.save()

        return self.payment_plan

    def lock_fsp(self) -> PaymentPlan:
        dm = getattr(self.payment_plan, "delivery_mechanism", None)
        fsp = getattr(self.payment_plan, "financial_service_provider", None)
        if not dm or not fsp:
            raise ValidationError("Payment Plan doesn't have FSP / DeliveryMechanism assigned.")

        if self.payment_plan.eligible_payments.filter(financial_service_provider__isnull=True).exists():
            self.payment_plan.eligible_payments.update(
                financial_service_provider=self.payment_plan.financial_service_provider,
                delivery_type=self.payment_plan.delivery_mechanism,
            )
        if self.payment_plan.eligible_payments.filter(entitlement_quantity__isnull=True).exists():
            raise ValidationError("All Payments must have entitlement quantity set.")

        self.payment_plan.status_lock_fsp()
        self.payment_plan.save()

        return self.payment_plan

    def unlock_fsp(self) -> Optional[PaymentPlan]:
        self.payment_plan.status_unlock_fsp()
        self.payment_plan.save()

        return self.payment_plan

    def acceptance_process(self) -> Optional[PaymentPlan]:
        self.validate_payment_plan_status_to_acceptance_process_approval_type()

        # every time we will create Approval for first created AcceptanceProcess
        # init creation AcceptanceProcess added in send_for_approval()
        approval_process = self.payment_plan.approval_process.first()
        if not approval_process:
            msg = f"Approval Process object not found for PaymentPlan {self.payment_plan.pk}"
            logging.exception(msg)
            raise ValidationError(msg)

        # validate approval required number and user as well
        self.validate_acceptance_process_approval_count(approval_process)

        approval_data = {
            "approval_process": approval_process,
            "created_by": self.user,
            "type": self.get_approval_type_by_action(),
            "comment": self.input_data.get("comment"),
        }
        Approval.objects.create(**approval_data)

        # base on approval required number check if we need update PaymentPlan status after creation new Approval
        self.check_payment_plan_and_update_status(approval_process)

        return self.payment_plan

    def validate_payment_plan_status_to_acceptance_process_approval_type(self) -> None:
        action_to_statuses_map = {
            PaymentPlan.Action.APPROVE.value: [PaymentPlan.Status.IN_APPROVAL],
            PaymentPlan.Action.AUTHORIZE.value: [PaymentPlan.Status.IN_AUTHORIZATION],
            PaymentPlan.Action.REVIEW.value: [PaymentPlan.Status.IN_REVIEW],
            PaymentPlan.Action.REJECT.value: [
                PaymentPlan.Status.IN_APPROVAL,
                PaymentPlan.Status.IN_AUTHORIZATION,
                PaymentPlan.Status.IN_REVIEW,
            ],
        }
        if self.action and self.payment_plan.status not in action_to_statuses_map[self.action]:
            raise ValidationError(
                f"Not possible to create {self.action} for Payment Plan within status {self.payment_plan.status}"
            )

    def validate_acceptance_process_approval_count(self, approval_process: ApprovalProcess) -> None:
        approval_type = self.get_approval_type_by_action()
        required_number = self.get_required_number_by_approval_type(approval_process)
        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            raise ValidationError(
                f"Can't create new approval. Required Number ({required_number}) of {approval_type} is already created"
            )
        # validate if the user can create approval
        # for test purposes this validation can be skipped
        if not config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS:
            approvals_by_user = approval_process.approvals.filter(created_by=self.user)

            # validate REJECT based on status payment plan
            if approval_type == Approval.REJECT:
                status_to_approval_type_map = {
                    PaymentPlan.Status.IN_APPROVAL: Approval.APPROVAL,
                    PaymentPlan.Status.IN_AUTHORIZATION.name: Approval.AUTHORIZATION,
                    PaymentPlan.Status.IN_REVIEW.name: Approval.FINANCE_RELEASE,
                }

                created_approval_type = status_to_approval_type_map[self.payment_plan.status]
                if approvals_by_user.filter(type=created_approval_type).exists():
                    raise ValidationError(
                        f"Can't create {approval_type}. User have already created {created_approval_type}"
                    )
            # validate other approval types
            elif approvals_by_user.filter(type=approval_type).exists():
                raise ValidationError(f"Can't create new {approval_type}. User have already created {approval_type}")

    def check_payment_plan_and_update_status(self, approval_process: ApprovalProcess) -> None:
        approval_type = self.get_approval_type_by_action()
        required_number = self.get_required_number_by_approval_type(approval_process)

        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            notification_action = None
            if approval_type == Approval.APPROVAL:
                self.payment_plan.status_approve()
                approval_process.sent_for_authorization_by = self.user
                approval_process.sent_for_authorization_date = timezone.now()
                approval_process.save()
                notification_action = PaymentPlan.Action.APPROVE

            if approval_type == Approval.AUTHORIZATION:
                self.payment_plan.status_authorize()
                approval_process.sent_for_finance_release_by = self.user
                approval_process.sent_for_finance_release_date = timezone.now()
                approval_process.save()
                notification_action = PaymentPlan.Action.AUTHORIZE

            if approval_type == Approval.FINANCE_RELEASE:
                self.payment_plan.status_mark_as_reviewed()
                notification_action = PaymentPlan.Action.REVIEW
                # remove imported and export files

            if approval_type == Approval.REJECT:
                self.payment_plan.status_reject()

            if notification_action:
                send_payment_notification_emails.delay(
                    self.payment_plan.id, notification_action.value, self.user.id, f"{timezone.now():%-d %B %Y}"
                )

            self.payment_plan.save()

    @staticmethod
    def create_payments(payment_plan: PaymentPlan) -> None:
        pp_split = payment_plan.splits.first()
        payments_to_create = []
        households = payment_plan.household_list

        households = (
            households.annotate(
                collector=IndividualRoleInHousehold.objects.filter(household=OuterRef("pk"), role=ROLE_PRIMARY).values(
                    "individual"
                )[:1]
            )
            .all()
            .values("pk", "collector", "unicef_id", "head_of_household")
        )
        for household in households:
            collector_id = household.get("collector")
            if not collector_id:
                msg = f"Couldn't find a primary collector in {household['unicef_id']}"
                logging.exception(msg)
                raise ValidationError(msg)
            collector = Individual.objects.get(id=collector_id)

            has_valid_wallet = True
            if payment_plan.delivery_mechanism and payment_plan.financial_service_provider:
                has_valid_wallet = PaymentDataCollector.validate_account(
                    payment_plan.financial_service_provider, payment_plan.delivery_mechanism, collector
                )

            payments_to_create.append(
                Payment(
                    parent=payment_plan,
                    parent_split=pp_split,
                    program_id=payment_plan.program_cycle.program_id,
                    business_area_id=payment_plan.business_area_id,
                    status=Payment.STATUS_PENDING,
                    status_date=timezone.now(),
                    household_id=household["pk"],
                    head_of_household_id=household["head_of_household"],
                    collector=collector,
                    financial_service_provider=payment_plan.financial_service_provider,
                    delivery_type=payment_plan.delivery_mechanism,
                    has_valid_wallet=has_valid_wallet,
                )
            )
        try:
            Payment.objects.bulk_create(payments_to_create)
        except IntegrityError as e:
            raise ValidationError("Duplicated Households in provided Targeting List") from e
        payment_plan.refresh_from_db()
        create_payment_plan_snapshot_data(payment_plan)
        PaymentPlanService.generate_signature(payment_plan)

    @staticmethod
    def generate_signature(payment_plan: PaymentPlan) -> None:
        payments = payment_plan.payment_items.select_related("household_snapshot").all()
        for payment in payments:
            payment.update_signature_hash()
        Payment.objects.bulk_update(payments, ["signature_hash"])

    @staticmethod
    def create_targeting_criteria(targeting_criteria_input: Dict, program: Program) -> TargetingCriteria:
        TargetingCriteriaInputValidator.validate(targeting_criteria_input, program)

        targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, program)

        return targeting_criteria

    @staticmethod
    def create(input_data: Dict, user: "User", business_area_slug: str) -> PaymentPlan:
        business_area = BusinessArea.objects.get(slug=business_area_slug)
        program_cycle = get_object_or_404(ProgramCycle, pk=input_data["program_cycle_id"])
        program = program_cycle.program
        if program_cycle.status == ProgramCycle.FINISHED:
            raise ValidationError("Impossible to create Target Population for Programme Cycle within Finished status")

        if program.status != Program.ACTIVE:
            raise ValidationError("Impossible to create Target Population for Programme within not Active status")

        pp_name = input_data.get("name", "").strip()
        if PaymentPlan.objects.filter(name=pp_name, program_cycle__program=program, is_removed=False).exists():
            raise ValidationError(f"Target Population with name: {pp_name} and program: {program.name} already exists.")

        with transaction.atomic():
            targeting_criteria = PaymentPlanService.create_targeting_criteria(input_data["targeting_criteria"], program)

            payment_plan = PaymentPlan.objects.create(
                business_area=business_area,
                created_by=user,
                program_cycle=program_cycle,
                targeting_criteria=targeting_criteria,
                name=input_data["name"],
                status_date=timezone.now(),
                start_date=program_cycle.start_date,
                end_date=program_cycle.end_date,
                status=PaymentPlan.Status.TP_OPEN,
                build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
                built_at=timezone.now(),
                excluded_ids=input_data.get("excluded_ids", "").strip(),
                exclusion_reason=input_data.get("exclusion_reason", "").strip(),
            )
            PaymentPlanSplit.objects.create(payment_plan=payment_plan)

            fsp_id = input_data.get("fsp_id")
            delivery_mechanism_code = input_data.get("delivery_mechanism_code")

            if fsp_id and delivery_mechanism_code:
                fsp = get_object_or_404(FinancialServiceProvider, pk=fsp_id)
                delivery_mechanism = get_object_or_404(DeliveryMechanism, code=delivery_mechanism_code)
                payment_plan.financial_service_provider = fsp
                payment_plan.delivery_mechanism = delivery_mechanism
                payment_plan.save(update_fields=["financial_service_provider", "delivery_mechanism"])

            transaction.on_commit(lambda: prepare_payment_plan_task.delay(str(payment_plan.id)))

        return payment_plan

    def update(self, input_data: Dict) -> PaymentPlan:
        program = self.payment_plan.program_cycle.program
        should_update_money_stats = False
        should_rebuild_list = False
        vulnerability_filter = False
        old_targeting_criteria = None

        name = input_data.get("name")
        vulnerability_score_min = input_data.get("vulnerability_score_min")
        vulnerability_score_max = input_data.get("vulnerability_score_max")
        excluded_ids = input_data.get("excluded_ids")
        exclusion_reason = input_data.get("exclusion_reason")
        targeting_criteria_input = input_data.get("targeting_criteria")
        dispersion_start_date = input_data.get("dispersion_start_date")
        dispersion_end_date = input_data.get("dispersion_end_date")
        fsp_id = input_data.get("fsp_id")
        delivery_mechanism_code = input_data.get("delivery_mechanism_code")

        if (
            any([excluded_ids, exclusion_reason, targeting_criteria_input])
            and not self.payment_plan.is_population_open()
        ):
            raise ValidationError(f"Not Allow edit targeting criteria within status {self.payment_plan.status}")

        if not self.payment_plan.is_population_locked() and (vulnerability_score_min or vulnerability_score_max):
            raise ValidationError(
                "You can only set vulnerability_score_min and vulnerability_score_max on Locked Population status"
            )

        if any(
            [dispersion_start_date, dispersion_end_date, input_data.get("currency")]
        ) and self.payment_plan.status not in [PaymentPlan.Status.OPEN, PaymentPlan.Status.DRAFT]:
            raise ValidationError(f"Not Allow edit Payment Plan within status {self.payment_plan.status}")

        if name:
            if self.payment_plan.status != PaymentPlan.Status.TP_OPEN:
                raise ValidationError("Name can be changed only within Open status")
            name = name.strip()

            if (
                PaymentPlan.objects.filter(name=name, program_cycle__program=program, is_removed=False)
                .exclude(id=self.payment_plan.pk)
                .exists()
            ):
                raise ValidationError(f"Name '{name}' and program '{program.name}' already exists.")
            self.payment_plan.name = name

        if self.payment_plan.is_follow_up:
            # can change only dispersion_start_date/dispersion_end_date for Follow Up Payment Plan
            # remove not editable fields
            input_data.pop("currency", None)

        if program_cycle_id := input_data.get("program_cycle_id"):
            program_cycle = get_object_or_404(ProgramCycle, pk=program_cycle_id)
            if program_cycle.status == ProgramCycle.FINISHED:
                raise ValidationError("Not possible to assign Finished Program Cycle")
            self.payment_plan.program_cycle = program_cycle

        if vulnerability_score_min != self.payment_plan.vulnerability_score_min:
            vulnerability_filter = True
            self.payment_plan.vulnerability_score_min = vulnerability_score_min
        if vulnerability_score_max != self.payment_plan.vulnerability_score_max:
            vulnerability_filter = True
            self.payment_plan.vulnerability_score_max = vulnerability_score_max

        if targeting_criteria_input:
            should_rebuild_list = True
            TargetingCriteriaInputValidator.validate(targeting_criteria_input, program)
            targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, program)
            if self.payment_plan.status == PaymentPlan.Status.TP_OPEN:
                if self.payment_plan.targeting_criteria:
                    old_targeting_criteria = self.payment_plan.targeting_criteria
                self.payment_plan.targeting_criteria = targeting_criteria
        if excluded_ids != self.payment_plan.excluded_ids:
            should_rebuild_list = True
            self.payment_plan.excluded_ids = excluded_ids
        if exclusion_reason != self.payment_plan.exclusion_reason:
            should_rebuild_list = True
            self.payment_plan.exclusion_reason = exclusion_reason

        if dispersion_start_date and dispersion_start_date != self.payment_plan.dispersion_start_date:
            self.payment_plan.dispersion_start_date = dispersion_start_date

        if dispersion_end_date and dispersion_end_date != self.payment_plan.dispersion_end_date:
            if dispersion_end_date <= timezone.now().date():
                raise ValidationError(f"Dispersion End Date [{dispersion_end_date}] cannot be a past date")
            self.payment_plan.dispersion_end_date = dispersion_end_date

        new_currency = input_data.get("currency")
        if new_currency and new_currency != self.payment_plan.currency:
            delivery_mechanism = self.payment_plan.delivery_mechanism
            if (
                new_currency == USDC
                and delivery_mechanism.transfer_type != DeliveryMechanism.TransferType.DIGITAL.value
            ) or (
                new_currency != USDC
                and delivery_mechanism.transfer_type == DeliveryMechanism.TransferType.DIGITAL.value
            ):
                raise ValidationError(
                    "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
                )
            self.payment_plan.currency = new_currency
            should_update_money_stats = True
            Payment.objects.filter(parent=self.payment_plan).update(currency=self.payment_plan.currency)

        if not (fsp_id and delivery_mechanism_code) and hasattr(self.payment_plan, "delivery_mechanism"):
            self.payment_plan.delivery_mechanism = None
            self.payment_plan.financial_service_provider = None
            should_rebuild_list = True

        if fsp_id and delivery_mechanism_code:
            fsp = get_object_or_404(FinancialServiceProvider, pk=fsp_id)
            delivery_mechanism = get_object_or_404(DeliveryMechanism, code=delivery_mechanism_code)
            if (
                self.payment_plan.financial_service_provider != fsp
                or self.payment_plan.delivery_mechanism != delivery_mechanism
            ):
                should_rebuild_list = True
                self.payment_plan.financial_service_provider = fsp
                self.payment_plan.delivery_mechanism = delivery_mechanism

        self.payment_plan.save()
        # remove old targeting_criteria
        if old_targeting_criteria:
            old_targeting_criteria.delete()

        # prevent race between commit transaction and using in task
        transaction.on_commit(
            lambda: PaymentPlanService.rebuild_payment_plan_population(
                should_rebuild_list, should_update_money_stats, vulnerability_filter, self.payment_plan
            )
        )
        return self.payment_plan

    def delete(self) -> PaymentPlan:
        if self.payment_plan.status not in [PaymentPlan.Status.OPEN, PaymentPlan.Status.TP_OPEN]:
            raise ValidationError("Deletion is only allowed when the status is 'Open'")

        if self.payment_plan.status == PaymentPlan.Status.OPEN:
            if self.payment_plan.program_cycle.payment_plans.count() == 1:
                # if it's the last Payment Plan in this Cycle need to update Cycle status
                # move from Active to Draft Cycle need to delete all Payment Plans
                self.payment_plan.program_cycle.set_draft()

            # with new proces just update status and not remove Payments and PaymentPlan
            self.payment_plan.status_draft()

        if self.payment_plan.status == PaymentPlan.Status.TP_OPEN:
            self.payment_plan.payment_items.all().delete()
            self.payment_plan.delete()

        self.payment_plan.save()

        return self.payment_plan

    def export_xlsx(self, user_id: "UUID") -> PaymentPlan:
        self.payment_plan.background_action_status_xlsx_exporting()
        self.payment_plan.save()

        create_payment_plan_payment_list_xlsx.delay(payment_plan_id=str(self.payment_plan.pk), user_id=str(user_id))
        self.payment_plan.refresh_from_db(fields=["background_action_status", "export_file_entitlement"])
        return self.payment_plan

    def export_xlsx_per_fsp(self, user_id: "UUID", fsp_xlsx_template_id: Optional[str]) -> PaymentPlan:
        self.payment_plan.background_action_status_xlsx_exporting()
        self.payment_plan.save()

        create_payment_plan_payment_list_xlsx_per_fsp.delay(
            str(self.payment_plan.pk), str(user_id), fsp_xlsx_template_id
        )
        self.payment_plan.refresh_from_db(fields=["background_action_status", "export_file_per_fsp"])
        return self.payment_plan

    def import_xlsx_per_fsp(self, user: Union["User", "AbstractBaseUser", "AnonymousUser"], file: IO) -> PaymentPlan:
        with transaction.atomic():
            self.payment_plan.background_action_status_xlsx_importing_reconciliation()
            self.payment_plan.save()

            file_temp = FileTemp.objects.create(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
                file=file,
            )
            transaction.on_commit(
                partial(
                    import_payment_plan_payment_list_per_fsp_from_xlsx.delay,
                    self.payment_plan.pk,
                    file_temp.pk,
                )
            )
        self.payment_plan.refresh_from_db()
        return self.payment_plan

    def create_follow_up_payments(self) -> None:
        self.payment_plan.exchange_rate = self.payment_plan.get_exchange_rate()
        self.payment_plan.save(update_fields=["exchange_rate"])
        payments_to_copy = self.payment_plan.source_payment_plan.unsuccessful_payments_for_follow_up()
        split = self.payment_plan.splits.first()
        follow_up_payments = [
            Payment(
                parent=self.payment_plan,
                parent_split=split,
                source_payment=payment,
                program_id=self.payment_plan.program_cycle.program_id,
                is_follow_up=True,
                business_area_id=payment.business_area_id,
                status=Payment.STATUS_PENDING,
                status_date=timezone.now(),
                household_id=payment.household_id,
                head_of_household_id=payment.head_of_household_id,
                collector_id=payment.collector_id,
                currency=payment.currency,
                entitlement_quantity=payment.entitlement_quantity,
                entitlement_quantity_usd=payment.entitlement_quantity_usd,
                financial_service_provider=self.payment_plan.financial_service_provider,
                delivery_type=self.payment_plan.delivery_mechanism,
            )
            for payment in payments_to_copy
        ]
        Payment.objects.bulk_create(follow_up_payments)
        create_payment_plan_snapshot_data(self.payment_plan)
        PaymentPlanService.generate_signature(self.payment_plan)

    @transaction.atomic
    def create_follow_up(
        self,
        user: Union["User", "AbstractBaseUser", "AnonymousUser"],
        dispersion_start_date: datetime.date,
        dispersion_end_date: datetime.date,
    ) -> PaymentPlan:
        source_pp = self.payment_plan

        if source_pp.is_follow_up:
            raise ValidationError("Cannot create a follow-up of a follow-up Payment Plan")

        if not source_pp.unsuccessful_payments().exists():
            raise ValidationError("Cannot create a follow-up for a payment plan with no unsuccessful payments")

        follow_up_pp = PaymentPlan.objects.create(
            name=source_pp.name + " Follow Up",
            status=PaymentPlan.Status.OPEN,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_OK,
            built_at=timezone.now(),
            status_date=timezone.now(),
            targeting_criteria=self.copy_target_criteria(source_pp.targeting_criteria),
            is_follow_up=True,
            source_payment_plan=source_pp,
            business_area=source_pp.business_area,
            created_by=user,
            program_cycle=source_pp.program_cycle,
            currency=source_pp.currency,
            dispersion_start_date=dispersion_start_date,
            dispersion_end_date=dispersion_end_date,
            start_date=source_pp.start_date,
            end_date=source_pp.end_date,
            delivery_mechanism=source_pp.delivery_mechanism,
            financial_service_provider=source_pp.financial_service_provider,
        )
        PaymentPlanSplit.objects.create(payment_plan=follow_up_pp)

        transaction.on_commit(lambda: prepare_follow_up_payment_plan_task.delay(follow_up_pp.id))

        return follow_up_pp

    def recalculate_signatures_in_batch(self, batch_size: int = 500) -> None:
        payment_plan = self.payment_plan
        payments_ids = list(payment_plan.eligible_payments.values_list("id", flat=True))
        for batch_start in range(0, len(payments_ids), batch_size):
            batched_ids = payments_ids[batch_start : batch_start + batch_size]
            payments = Payment.objects.filter(id__in=batched_ids).select_related("household_snapshot")
            for payment in payments:
                payment.update_signature_hash()
            Payment.objects.bulk_update(payments, ("signature_hash",))

    def split(self, split_type: str, chunks_no: Optional[int] = None) -> PaymentPlan:
        payments_chunks = []
        payments = self.payment_plan.eligible_payments.all()
        payments_count = payments.count()
        if not payments_count:
            raise ValidationError("No payments to split")

        if split_type == PaymentPlanSplit.SplitType.BY_RECORDS:
            if not chunks_no:
                raise ValidationError("Payments Number is required for split by records")

            if chunks_no > payments_count or chunks_no < PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK:
                raise ValidationError(
                    f"Payment Parts number should be between {PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK} and total number of payments"
                )
            payments_chunks = list(chunks(list(payments.order_by("unicef_id")), chunks_no))

        elif split_type in [
            PaymentPlanSplit.SplitType.BY_ADMIN_AREA1,
            PaymentPlanSplit.SplitType.BY_ADMIN_AREA2,
            PaymentPlanSplit.SplitType.BY_ADMIN_AREA3,
        ]:
            area_level = split_type[-1]
            grouped_payments = list(
                payments.order_by(f"household__admin{area_level}__p_code", "unicef_id").select_related(
                    f"household__admin{area_level}"
                )
            )
            payments_chunks = []
            for _, payments in groupby(grouped_payments, key=lambda x: getattr(x.household, f"admin{area_level}")):  # type: ignore
                payments_chunks.append(list(payments))

        elif split_type == PaymentPlanSplit.SplitType.BY_COLLECTOR:
            grouped_payments = list(payments.order_by("collector__unicef_id", "unicef_id").select_related("collector"))
            payments_chunks = []
            for _, payments in groupby(grouped_payments, key=lambda x: x.collector):  # type: ignore
                payments_chunks.append(list(payments))

        elif split_type == PaymentPlanSplit.SplitType.NO_SPLIT:
            payments_chunks = [list(payments)]

        payments_chunks_count = len(payments_chunks)
        if payments_chunks_count > PaymentPlanSplit.MAX_CHUNKS:
            raise ValidationError(
                f"Too many Payment Parts to split: {payments_chunks_count}, maximum is {PaymentPlanSplit.MAX_CHUNKS}"
            )

        with transaction.atomic():
            if self.payment_plan.splits.exists():
                self.payment_plan.splits.all().delete()
            if self.payment_plan.export_file_per_fsp:
                self.payment_plan.remove_export_file_per_fsp()

            payment_plan_splits_to_create = []
            for i, _ in enumerate(payments_chunks):
                payment_plan_splits_to_create.append(
                    PaymentPlanSplit(
                        payment_plan=self.payment_plan,
                        split_type=split_type,
                        chunks_no=chunks_no,
                        order=i,
                    )
                )
            PaymentPlanSplit.objects.bulk_create(payment_plan_splits_to_create)
            for i, chunk in enumerate(payments_chunks):
                payment_plan_splits_to_create[i].split_payment_items.set(chunk)

        return self.payment_plan

    def full_rebuild(self) -> None:
        payment_plan: PaymentPlan = self.payment_plan
        # remove all payment and recreate
        payment_plan.payment_items(manager="all_objects").all().delete()

        self.create_payments(payment_plan)

        payment_plan.update_population_count_fields()

    @staticmethod
    def rebuild_payment_plan_population(
        rebuild_list: bool, should_update_money_stats: bool, vulnerability_filter: bool, payment_plan: PaymentPlan
    ) -> None:
        rebuild_full_list = payment_plan.status in PaymentPlan.PRE_PAYMENT_PLAN_STATUSES and rebuild_list
        payment_plan.build_status_pending()
        payment_plan.save(update_fields=("build_status", "built_at"))

        if rebuild_full_list:
            payment_plan_full_rebuild.delay(str(payment_plan.id))

        if should_update_money_stats:
            payment_plan_rebuild_stats.delay(str(payment_plan.id))

        if vulnerability_filter:
            # just remove all with vulnerability_score filter
            params = {}
            if payment_plan.vulnerability_score_max is not None:
                params["vulnerability_score__lte"] = payment_plan.vulnerability_score_max
            if payment_plan.vulnerability_score_min is not None:
                params["vulnerability_score__gte"] = payment_plan.vulnerability_score_min
            payment_plan.payment_items(manager="all_objects").filter(**params).update(is_removed=False)
            payment_plan.payment_items(manager="all_objects").exclude(**params).update(is_removed=True)
            payment_plan_rebuild_stats.delay(str(payment_plan.id))

    @staticmethod
    def copy_target_criteria(targeting_criteria: TargetingCriteria) -> TargetingCriteria:
        targeting_criteria_copy = TargetingCriteria()
        targeting_criteria_copy.save()
        for rule in targeting_criteria.rules.all():
            rule_copy = TargetingCriteriaRule(
                targeting_criteria=targeting_criteria_copy,
                household_ids=rule.household_ids,
                individual_ids=rule.individual_ids,
            )
            rule_copy.save()
            for hh_filter in rule.filters.all():
                hh_filter.pk = None
                hh_filter.targeting_criteria_rule = rule_copy
                hh_filter.save()
            for ind_filter_block in rule.individuals_filters_blocks.all():
                ind_filter_block_copy = TargetingIndividualRuleFilterBlock(
                    targeting_criteria_rule=rule_copy, target_only_hoh=ind_filter_block.target_only_hoh
                )
                ind_filter_block_copy.save()
                for ind_filter in ind_filter_block.individual_block_filters.all():
                    ind_filter.pk = None
                    ind_filter.individuals_filters_block = ind_filter_block_copy
                    ind_filter.save()

            for col_filter_block in rule.collectors_filters_blocks.all():
                col_filter_block_copy = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=rule_copy)
                col_filter_block_copy.save()
                for col_filter in col_filter_block.collector_block_filters.all():
                    col_filter.pk = None
                    col_filter.collector_block_filters = col_filter_block_copy
                    col_filter.save()

        return targeting_criteria_copy

    def send_xlsx_password(self) -> PaymentPlan:
        send_payment_plan_payment_list_xlsx_per_fsp_password.delay(str(self.payment_plan.pk), str(self.user.pk))
        return self.payment_plan
