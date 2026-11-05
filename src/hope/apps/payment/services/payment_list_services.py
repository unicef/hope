import datetime
from decimal import Decimal
from itertools import groupby
import logging
from typing import TYPE_CHECKING, Any, Callable, Union, cast
from uuid import UUID

from constance import config
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import (
    BooleanField,
    Case,
    DateField,
    Exists,
    ExpressionWrapper,
    F,
    OuterRef,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from requests import RequestException
from rest_framework.exceptions import ValidationError
from rest_framework.status import is_client_error
from viewflow.fsm import NoTransition

from hope.apps.account.permissions import Permissions
from hope.apps.core.exchange_rates import ExchangeRates
from hope.apps.core.utils import chunks
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.apps.payment.celery_tasks import (
    create_payment_list_xlsx_async_task,
    payment_list_full_rebuild_async_task,
    payment_list_rebuild_stats_async_task,
    payment_list_refresh_payees_async_task,
    prepare_child_payment_list_async_task,
    prepare_payment_list_async_task,
    send_payment_list_reconciliation_overdue_email_async_task,
    send_to_payment_gateway_async_task,
)
from hope.apps.payment.flows import PaymentListFlow
from hope.apps.payment.services.payment_household_snapshot_service import (
    create_payment_list_snapshot_data,
)
from hope.apps.payment.utils import get_link, get_quantity_in_usd
from hope.apps.targeting.services.utils import from_input_to_targeting_criteria
from hope.apps.targeting.validators import TargetingCriteriaInputValidator
from hope.apps.utils.recipients import users_with_permissions
from hope.models import (
    Approval,
    ApprovalProcess,
    Currency,
    DeliveryMechanism,
    Household,
    Individual,
    IndividualRoleInHousehold,
    Payment,
    PaymentDataCollector,
    PaymentHouseholdSnapshot,
    PaymentList,
    PaymentListSplit,
    PaymentPlan,
    Program,
    ProgramCycle,
    TargetingCriteriaRule,
    TargetingIndividualRuleFilterBlock,
    User,
)

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import QuerySet

    from hope.models import FollowUpInstruction

logger = logging.getLogger(__name__)


ACTION_TO_APPROVAL_TYPE = {
    PaymentList.Action.APPROVE.value: Approval.APPROVAL,
    PaymentList.Action.AUTHORIZE.value: Approval.AUTHORIZATION,
    PaymentList.Action.REVIEW.value: Approval.FINANCE_RELEASE,
    PaymentList.Action.REJECT.value: Approval.REJECT,
}
APPROVAL_TYPE_FOR_STATUS = {
    "IN_APPROVAL": Approval.APPROVAL,
    "IN_AUTHORIZATION": Approval.AUTHORIZATION,
    "IN_REVIEW": Approval.FINANCE_RELEASE,
}
STAGE_REACHED_NOTIFICATION = {
    Approval.APPROVAL: PaymentList.Action.APPROVE,
    Approval.AUTHORIZATION: PaymentList.Action.AUTHORIZE,
    Approval.FINANCE_RELEASE: PaymentList.Action.REVIEW,
}


def required_number_for(approval_process: ApprovalProcess, approval_type: str) -> int:
    return {
        Approval.APPROVAL: approval_process.approval_number_required,
        Approval.AUTHORIZATION: approval_process.authorization_number_required,
        Approval.FINANCE_RELEASE: approval_process.finance_release_number_required,
        Approval.REJECT: 1,  # only one Reject per Acceptance Process object
    }[approval_type]


def validate_approval_count(
    approval_process: ApprovalProcess,
    approval_type: str,
    required_number: int,
    current_status: str,
    user: "User | None",
) -> None:
    if approval_process.approvals.filter(type=approval_type).count() >= required_number:
        raise ValidationError(
            f"Can't create new approval. Required Number ({required_number}) of {approval_type} is already created"
        )
    if config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS:
        return
    approvals_by_user = approval_process.approvals.filter(created_by=user)
    if approval_type == Approval.REJECT:
        created_approval_type = APPROVAL_TYPE_FOR_STATUS[current_status]
        if approvals_by_user.filter(type=created_approval_type).exists():
            raise ValidationError(f"Can't create {approval_type}. User have already created {created_approval_type}")
    elif approvals_by_user.filter(type=approval_type).exists():
        raise ValidationError(f"Can't create new {approval_type}. User have already created {approval_type}")


def record_stage_reached(approval_process: ApprovalProcess, approval_type: str, user: "User | None") -> None:
    if approval_type == Approval.APPROVAL:
        approval_process.sent_for_authorization_by = user
        approval_process.sent_for_authorization_date = timezone.now()
        approval_process.save()
    if approval_type == Approval.AUTHORIZATION:
        approval_process.sent_for_finance_release_by = user
        approval_process.sent_for_finance_release_date = timezone.now()
        approval_process.save()


class PaymentListService:
    def __init__(self, payment_list: "PaymentList"):
        self.payment_list = payment_list

        self.action: str | None = None
        self.user: User | None = None
        self.input_data: dict | None = None

    @property
    def actions_map(self) -> dict:
        return {
            # old TP
            PaymentList.Action.TP_LOCK.value: self.tp_lock,
            PaymentList.Action.TP_UNLOCK.value: self.tp_unlock,
            PaymentList.Action.TP_REBUILD.value: self.tp_rebuild,
            PaymentList.Action.DRAFT.value: self.draft,
            # PP
            PaymentList.Action.LOCK.value: self.lock,
            PaymentList.Action.LOCK_FSP.value: self.lock_fsp,
            PaymentList.Action.UNLOCK.value: self.unlock,
            PaymentList.Action.UNLOCK_FSP.value: self.unlock_fsp,
            PaymentList.Action.SEND_TO_PAYMENT_GATEWAY.value: self.send_to_payment_gateway,
        }

    def execute_update_status_action(
        self,
        input_data: dict,
        user: "AbstractBaseUser | AnonymousUser",
        as_manager: bool = False,
    ) -> PaymentList:
        """Run the action named in ``input_data`` on the plan and return it.

        A plan's workflow belongs to its manager — its Payment Plan once that is no longer OPEN, or its
        Follow-Up Instruction. A user acting on the plan itself is refused then; the manager (and the system,
        e.g. Vision or an admin retry) passes ``as_manager=True``.
        """
        if not as_manager:
            if self.payment_list.is_instruction_managed:
                raise ValidationError("This Payment List is managed by a Follow Up Instruction.")
            self.validate_payment_plan_open()
        self.action = input_data.get("action")
        self.input_data = input_data
        self.user = cast("User", user)
        self.validate_action()

        function_action = self.get_action_function()
        try:
            return function_action()
        except NoTransition:
            action_label = PaymentList.Action(cast("str", self.action)).label
            raise ValidationError(
                f"{action_label} is not allowed when the Payment List status is "
                f"{self.payment_list.get_status_display()}."
            )

    def validate_payment_plan_open(self) -> None:
        """Refuse a list change once the list's Payment Plan is no longer OPEN.

        The plan row is read with a row lock, so a change sent while Lock Payment Plan is running waits for it and is
        refused, instead of saving the list over the LOCKED_FSP status the lock gave it.
        """
        if self.payment_list.payment_plan_id is None:
            return
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.payment_list.payment_plan_id)
        if payment_plan.status != PaymentPlan.Status.OPEN:
            raise ValidationError("This Payment List is managed by its Payment Plan.")

    def validate_action(self) -> None:
        actions = list(self.actions_map.keys())
        if self.action not in actions:
            raise ValidationError(f"Not Implemented Action: {self.action}. List of possible actions: {actions}")

    def get_action_function(self) -> Callable | None:
        return self.actions_map.get(self.action)

    def transition_send_for_approval(self) -> None:
        """Move the plan to IN_APPROVAL; the approval process and the notification belong to the caller."""
        background_action_status = self.payment_list.background_action_status
        if (
            background_action_status is not None
            and background_action_status not in PaymentList.BACKGROUND_ACTION_ERROR_STATES
        ):
            raise ValidationError("Another background action is already in progress.")
        flow = PaymentListFlow(self.payment_list)
        if background_action_status in PaymentList.BACKGROUND_ACTION_ERROR_STATES:
            flow.background_action_status_none()
        flow.status_send_to_approval()
        self.payment_list.save()

    def send_to_payment_gateway(self) -> PaymentList:
        with transaction.atomic():
            payment_list = PaymentList.objects.select_for_update().get(pk=self.payment_list.pk)

            if payment_list.background_action_status == PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY:
                raise ValidationError("Sending in progress")
            if not payment_list.can_send_to_payment_gateway:
                raise ValidationError("Already sent to Payment Gateway")

            flow = PaymentListFlow(payment_list)
            flow.background_action_status_send_to_payment_gateway()
            payment_list.save(update_fields=["background_action_status"])

            transaction.on_commit(lambda: send_to_payment_gateway_async_task(payment_list, str(self.user.pk)))

        self.payment_list = payment_list
        return self.payment_list

    def tp_lock(self) -> PaymentList:
        if self.payment_list.build_status != PaymentList.BuildStatus.BUILD_STATUS_OK:
            raise ValidationError("Can only be locked when Build Status OK")
        flow = PaymentListFlow(self.payment_list)
        flow.status_tp_lock()
        self.payment_list.save(update_fields=("status", "status_date", "updated_at"))

        return self.payment_list

    def tp_unlock(self) -> PaymentList:
        flow = PaymentListFlow(self.payment_list)
        flow.status_tp_open()
        flow.build_status_pending()
        self.payment_list.save(update_fields=("build_status", "built_at", "status", "status_date", "updated_at"))
        transaction.on_commit(lambda: payment_list_rebuild_stats_async_task(self.payment_list))

        return self.payment_list

    def tp_rebuild(self) -> PaymentList:
        if self.payment_list.status not in [
            PaymentList.Status.TP_OPEN,
            PaymentList.Status.TP_LOCKED,
        ]:
            raise ValidationError("Can only Rebuild Population for Locked or Open Population status")

        flow = PaymentListFlow(self.payment_list)
        flow.build_status_pending()
        self.payment_list.save(update_fields=("build_status", "built_at", "updated_at"))
        transaction.on_commit(lambda: payment_list_full_rebuild_async_task(self.payment_list))
        return self.payment_list

    def draft(self) -> PaymentList:
        if not self.payment_list.financial_service_provider:
            raise ValidationError(
                "Can only promote to Payment List if the Payment Plan has a Financial Service Provider."
            )
        flow = PaymentListFlow(self.payment_list)
        flow.status_draft()
        self.payment_list.save(update_fields=("status_date", "status", "updated_at"))
        return self.payment_list

    def open(self) -> PaymentList:
        flow = PaymentListFlow(self.payment_list)
        flow.status_open()
        payment_plan = self.payment_list.payment_plan
        if payment_plan is None or payment_plan.currency_id is None:
            raise ValidationError("Payment Plan needs a Currency before a Payment List can be opened.")
        dispersion_end_date = payment_plan.dispersion_end_date
        if payment_plan.dispersion_start_date is None or dispersion_end_date is None:
            raise ValidationError("Payment Plan needs Dispersion Dates before a Payment List can be opened.")
        if dispersion_end_date <= timezone.now().date():
            raise ValidationError(f"Dispersion End Date [{dispersion_end_date}] cannot be a past date")
        if payment_plan.exchange_rate is None:
            try:
                payment_plan.exchange_rate = self.payment_list.get_exchange_rate()
            except RequestException as e:
                if e.response is not None and is_client_error(e.response.status_code):
                    logger.error("UNORE rejected exchange rate request for PaymentList %s: %s", self.payment_list.pk, e)
                else:
                    logger.warning(
                        "Failed to fetch UNORE exchange rate for PaymentList %s: %s", self.payment_list.pk, e
                    )
                payment_plan.exchange_rate = None
            payment_plan.save(update_fields=("exchange_rate", "updated_at"))

        self.payment_list.save(update_fields=("status_date", "status", "updated_at"))
        self.payment_list.program_cycle.set_active()

        Payment.objects.filter(parent=self.payment_list).update(currency=payment_plan.currency)
        self.payment_list.update_money_fields()

        return self.payment_list

    def lock(self) -> PaymentList:
        if not self.payment_list.can_be_locked:
            raise ValidationError("At least one valid Payment should exist in order to Lock the Payment List")

        user_id = str(self.user.pk) if self.user else None
        self.payment_list.eligible_payments_with_conflicts.filter(payment_list_hard_conflicted=True).update_and_log(
            {
                "conflicted": True,
                "status": Payment.STATUS_NOT_ELIGIBLE,
                "status_date": timezone.now(),
            },
            user_id,
        )
        flow = PaymentListFlow(self.payment_list)
        flow.status_lock()
        self.payment_list.update_population_count_fields()
        self.payment_list.update_money_fields()

        self.payment_list.save()

        return self.payment_list

    def clear_lock_conflicts(self) -> None:
        """Undo what lock() did to hard-conflicted payments."""
        restorable_payments = self.payment_list.payment_items.filter(
            status=Payment.STATUS_NOT_ELIGIBLE,
            excluded=False,
            has_valid_wallet=True,
        )
        user_id = str(self.user.pk) if self.user else None
        restorable_payments.update_and_log(
            {
                "conflicted": False,
                "status": Payment.STATUS_PENDING,
                "status_date": timezone.now(),
            },
            user_id,
        )
        self.payment_list.payment_items.filter(conflicted=True).update_and_log({"conflicted": False}, user_id)

    def unlock(self) -> PaymentList:
        self.clear_lock_conflicts()
        flow = PaymentListFlow(self.payment_list)
        flow.status_unlock()
        self.payment_list.update_population_count_fields()
        self.payment_list.update_money_fields()
        self.payment_list.remove_export_files()

        self.payment_list.save()

        return self.payment_list

    def lock_fsp(self) -> PaymentList:
        dm = getattr(self.payment_list, "delivery_mechanism", None)
        fsp = getattr(self.payment_list, "financial_service_provider", None)
        if not dm or not fsp:
            raise ValidationError("Payment List doesn't have FSP / DeliveryMechanism assigned.")
        background_action_status = self.payment_list.background_action_status
        if (
            background_action_status is not None
            and background_action_status not in PaymentList.BACKGROUND_ACTION_ERROR_STATES
        ):
            raise ValidationError("Another background action is already in progress.")

        if self.payment_list.eligible_payments.filter(financial_service_provider__isnull=True).exists():
            self.payment_list.eligible_payments.update(
                financial_service_provider=self.payment_list.financial_service_provider,
                delivery_type=self.payment_list.delivery_mechanism,
            )
        if self.payment_list.eligible_payments.filter(entitlement_quantity__isnull=True).exists():
            raise ValidationError("All Payments must have entitlement quantity set.")

        flow = PaymentListFlow(self.payment_list)
        flow.status_lock_fsp()
        self.payment_list.save()

        return self.payment_list

    def unlock_fsp(self) -> PaymentList | None:
        background_action_status = self.payment_list.background_action_status
        if (
            background_action_status is not None
            and background_action_status not in PaymentList.BACKGROUND_ACTION_ERROR_STATES
        ):
            raise ValidationError("Another background action is already in progress.")
        flow = PaymentListFlow(self.payment_list)
        if background_action_status in PaymentList.BACKGROUND_ACTION_ERROR_STATES:
            flow.background_action_status_none()
        flow.status_unlock_fsp()
        self.payment_list.save()

        return self.payment_list

    def apply_acceptance_stage(self, approval_type: str, user: "User") -> None:
        """Move the plan to the stage whose approval count was just reached, with the per-plan side effects.

        Shared by the plan's own acceptance process and by the payment plan's, which walks every plan through it.
        """
        flow = PaymentListFlow(self.payment_list)
        if approval_type == Approval.APPROVAL:
            flow.status_approve()
        if approval_type == Approval.AUTHORIZATION:
            flow.status_authorize()
        if approval_type == Approval.FINANCE_RELEASE:
            flow.status_mark_as_reviewed()
        if approval_type == Approval.REJECT:
            flow.status_reject()

        self.payment_list.save()

    @staticmethod
    def create_payments(payment_list: PaymentList) -> None:
        if not (pp_split := payment_list.splits.first()):
            pp_split = PaymentListSplit.objects.create(payment_list=payment_list)

        payments_to_create = []
        household_rows, collectors_by_id, wallet_validity_by_collector_id = PaymentListService._resolve_collectors(
            payment_list, payment_list.household_list
        )
        delivery_mechanism = payment_list.delivery_mechanism
        financial_service_provider = payment_list.financial_service_provider

        for household in household_rows:
            collector, collector_type = PaymentListService._get_collector(household, collectors_by_id)

            payments_to_create.append(
                Payment(
                    parent=payment_list,
                    parent_split=pp_split,
                    program_id=payment_list.program_cycle.program_id,
                    business_area_id=payment_list.business_area_id,
                    status=(
                        Payment.STATUS_PENDING
                        if wallet_validity_by_collector_id[collector.id]
                        else Payment.STATUS_NOT_ELIGIBLE
                    ),
                    status_date=timezone.now(),
                    household_id=household["pk"],
                    head_of_household_id=household["head_of_household"],
                    collector=collector,
                    collector_type=collector_type,
                    currency=payment_list.currency,
                    financial_service_provider=financial_service_provider,
                    delivery_type=delivery_mechanism,
                    has_valid_wallet=wallet_validity_by_collector_id[collector.id],
                )
            )
        try:
            Payment.objects.bulk_create(payments_to_create)
        except IntegrityError as e:
            raise ValidationError("Duplicated Households in provided Targeting List") from e
        payment_list.refresh_from_db()
        create_payment_list_snapshot_data(payment_list)
        PaymentListService.generate_signature(payment_list)

    @staticmethod
    def _resolve_collectors(
        payment_list: PaymentList, households: "QuerySet"
    ) -> tuple[list[dict[str, Any]], dict[UUID, Individual], dict[UUID, bool]]:
        """Pick each household's collector and check its wallet against the plan's FSP and delivery mechanism."""
        use_alt_collector_set = {
            i.strip()
            for row in payment_list.rules.all().values_list("alternative_collectors_ids", flat=True)
            if row
            for i in row.split(",")
            if i.strip()
        }
        hh_ids = {i for i in use_alt_collector_set if i.startswith("HH")}
        ind_ids = {i for i in use_alt_collector_set if i.startswith("IND")}

        individuals_match = Individual.objects.filter(
            household_id=OuterRef("pk"),
            unicef_id__in=ind_ids,
        )
        household_rows = list(
            households.annotate(
                pr_collector=IndividualRoleInHousehold.objects.filter(
                    household=OuterRef("pk"), role=ROLE_PRIMARY
                ).values("individual")[:1],
                alt_collector=IndividualRoleInHousehold.objects.filter(
                    household=OuterRef("pk"), role=ROLE_ALTERNATE
                ).values("individual")[:1],
                individuals_unicef_ids=ArrayAgg("individuals__unicef_id"),
                use_alt_collector=Case(
                    When(unicef_id__in=hh_ids, then=Value(True)),
                    When(Exists(individuals_match), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
            .all()
            .values("pk", "pr_collector", "alt_collector", "unicef_id", "head_of_household", "use_alt_collector")
        )

        collector_ids = {
            household["alt_collector"] if household["use_alt_collector"] else household["pr_collector"]
            for household in household_rows
        }
        collector_ids.discard(None)
        collectors_by_id = {
            collector.id: collector
            for collector in Individual.objects.filter(id__in=collector_ids).select_related("household__country")
        }
        wallet_validity_by_collector_id = PaymentDataCollector.validate_accounts(
            payment_list.financial_service_provider,
            payment_list.delivery_mechanism,
            collectors_by_id.values(),
        )
        return household_rows, collectors_by_id, wallet_validity_by_collector_id

    @staticmethod
    def _get_collector(
        household: dict[str, Any],
        collectors_by_id: dict[UUID, Individual] | None = None,
    ) -> tuple[Individual, str]:
        use_alt_collector = household.get("use_alt_collector", False)
        if use_alt_collector:
            collector_id = household.get("alt_collector")
            collector_type = ROLE_ALTERNATE
        else:
            collector_id = household.get("pr_collector")
            collector_type = ROLE_PRIMARY

        if not collector_id:
            msg = f"Couldn't find a {collector_type} collector in {household['unicef_id']}"
            logging.exception(msg)
            raise ValidationError(msg)

        collector = collectors_by_id.get(collector_id) if collectors_by_id is not None else None
        if collector is None:
            collector = Individual.objects.get(id=collector_id)
        return collector, collector_type

    @staticmethod
    def generate_signature(payment_list: PaymentList) -> None:
        payments_queryset = payment_list.eligible_payments.select_related(
            "household_snapshot", "currency", "delivery_type"
        ).all()
        paginator = Paginator(payments_queryset, 500)
        for page_number in paginator.page_range:
            payments = paginator.page(page_number).object_list
            for payment in payments:
                payment.update_signature_hash()
            Payment.objects.bulk_update(payments, ["signature_hash"])

    def create_targeting_criteria(self, targeting_criteria_input: dict, program: Program) -> None:
        TargetingCriteriaInputValidator.validate(targeting_criteria_input, program)

        # Update the payment plan with targeting criteria fields
        self.payment_list.flag_exclude_if_active_adjudication_ticket = targeting_criteria_input.get(
            "flag_exclude_if_active_adjudication_ticket", False
        )
        self.payment_list.flag_exclude_if_on_sanction_list = targeting_criteria_input.get(
            "flag_exclude_if_on_sanction_list", False
        )
        self.payment_list.save()

        from_input_to_targeting_criteria(targeting_criteria_input, program, self.payment_list)

    @staticmethod
    def create(input_data: dict, user: "User", program: Program) -> PaymentList:
        business_area = program.business_area
        program_cycle = get_object_or_404(ProgramCycle, pk=input_data["program_cycle_id"], program=program)
        if program_cycle.status == ProgramCycle.FINISHED:
            raise ValidationError("Impossible to create Target Population for Programme Cycle within Finished status")

        if program.status != Program.ACTIVE:
            raise ValidationError("Impossible to create Target Population for Programme within not Active status")

        pp_name = input_data.get("name", "").strip()
        if PaymentList.objects.filter(name=pp_name, program_cycle__program=program, is_removed=False).exists():
            raise ValidationError(f"Target Population with name: {pp_name} and program: {program.name} already exists.")

        with transaction.atomic():
            # Locked so the plan cannot be locked while this list joins it.
            payment_plan = (
                PaymentPlan.objects.select_for_update()
                .filter(pk=input_data["payment_plan_id"], cycle=program_cycle)
                .first()
            )
            if payment_plan is None:
                raise ValidationError("Payment Plan does not exist in the given Programme Cycle.")
            PaymentListService._validate_payment_plan_accepts_new_payment_lists(payment_plan)
            payment_list = PaymentList.objects.create(
                business_area=business_area,
                created_by=user,
                program_cycle=program_cycle,
                payment_plan=payment_plan,
                name=input_data["name"],
                status_date=timezone.now(),
                start_date=program_cycle.start_date,
                end_date=program_cycle.end_date,
                status=PaymentList.Status.TP_OPEN,
                build_status=PaymentList.BuildStatus.BUILD_STATUS_PENDING,
                built_at=timezone.now(),
                excluded_ids=input_data.get("excluded_ids", "").strip(),
                exclusion_reason=input_data.get("exclusion_reason", "").strip(),
            )

            payment_list.payment_plan_purposes.set(input_data["payment_plan_purposes"])

            if delivery_mechanism_code := input_data.get("delivery_mechanism_code"):
                payment_list.delivery_mechanism = PaymentListService._get_delivery_mechanism_for_payment_plan(
                    payment_plan, delivery_mechanism_code
                )
                payment_list.save(update_fields=["delivery_mechanism", "updated_at"])

            targeting_criteria_data = {
                "rules": input_data["rules"],
                "flag_exclude_if_on_sanction_list": input_data["flag_exclude_if_on_sanction_list"],
                "flag_exclude_if_active_adjudication_ticket": input_data["flag_exclude_if_active_adjudication_ticket"],
            }
            PaymentListService(payment_list).create_targeting_criteria(targeting_criteria_data, program)

            transaction.on_commit(lambda: prepare_payment_list_async_task(payment_list))

        return payment_list

    def _validate_update_permissions(self, input_data: dict) -> None:
        excluded_ids = input_data.get("excluded_ids")
        exclusion_reason = input_data.get("exclusion_reason")
        rules = input_data.get("rules")
        vulnerability_score_min = input_data.get("vulnerability_score_min")
        vulnerability_score_max = input_data.get("vulnerability_score_max")

        self._validate_pp_status(
            excluded_ids,
            exclusion_reason,
            input_data,
            rules=rules,
            vulnerability_score_max=vulnerability_score_max,
            vulnerability_score_min=vulnerability_score_min,
        )

    def _update_delivery_mechanism(self, delivery_mechanism_code: str | None) -> bool:
        if not self.payment_list.is_population_open():
            return False
        if not delivery_mechanism_code:
            if self.payment_list.delivery_mechanism_id is None:
                return False
            self.payment_list.delivery_mechanism = None
            return True
        delivery_mechanism = self._get_delivery_mechanism_for_payment_plan(
            self.payment_list.payment_plan, delivery_mechanism_code
        )
        if delivery_mechanism == self.payment_list.delivery_mechanism:
            return False
        self.payment_list.delivery_mechanism = delivery_mechanism
        return True

    @staticmethod
    def _get_delivery_mechanism_for_payment_plan(
        payment_plan: PaymentPlan | None, delivery_mechanism_code: str
    ) -> DeliveryMechanism:
        delivery_mechanism = get_object_or_404(DeliveryMechanism, code=delivery_mechanism_code)
        if payment_plan is not None and (currency := payment_plan.currency) is not None:
            PaymentListService.validate_currency_for_delivery_mechanism(currency, delivery_mechanism)
        return delivery_mechanism

    def _set_vulnerability_scores(self, input_data: dict) -> bool:
        """Apply vulnerability score bounds; return whether either changed."""
        vulnerability_filter = False
        vulnerability_score_min = input_data.get("vulnerability_score_min")
        vulnerability_score_max = input_data.get("vulnerability_score_max")
        if vulnerability_score_min != self.payment_list.vulnerability_score_min:
            vulnerability_filter = True
            self.payment_list.vulnerability_score_min = vulnerability_score_min
        if vulnerability_score_max != self.payment_list.vulnerability_score_max:
            vulnerability_filter = True
            self.payment_list.vulnerability_score_max = vulnerability_score_max
        return vulnerability_filter

    @transaction.atomic
    def update(self, input_data: dict) -> PaymentList:
        program = self.payment_list.program_cycle.program
        should_rebuild_list = False

        self._validate_update_permissions(input_data)

        name = input_data.get("name")
        rules = input_data.get("rules")

        if name:
            name = self._validate_pp_name(name, program)
            self.payment_list.name = name

        fsp_id_before = self.payment_list.payment_plan.financial_service_provider_id
        self._set_program_cycle(input_data)
        self._set_payment_plan_for_open_payment_list(input_data)
        if self.payment_list.payment_plan.financial_service_provider_id != fsp_id_before:
            should_rebuild_list = True

        vulnerability_filter = self._set_vulnerability_scores(input_data)

        if rules and self.payment_list.status == PaymentList.Status.TP_OPEN:
            targeting_criteria_input = {"rules": input_data["rules"]}
            self._set_additional_flags_for_tp(input_data, targeting_criteria_input)
            should_rebuild_list = True
            self.payment_list.rules.all().delete()
            self.create_targeting_criteria(targeting_criteria_input, program)

        excluded_ids, exclusion_reason = input_data.get("excluded_ids"), input_data.get("exclusion_reason")
        if excluded_ids != self.payment_list.excluded_ids:
            should_rebuild_list = True
            self.payment_list.excluded_ids = excluded_ids
        if exclusion_reason != self.payment_list.exclusion_reason:
            should_rebuild_list = True
            self.payment_list.exclusion_reason = exclusion_reason

        if self._update_delivery_mechanism(input_data.get("delivery_mechanism_code")):
            should_rebuild_list = True

        self.payment_list.save()

        self._update_purposes(input_data.get("payment_plan_purposes"))

        # prevent race between commit transaction and using in task
        transaction.on_commit(
            lambda: PaymentListService.rebuild_payment_list_population(
                should_rebuild_list,
                False,
                vulnerability_filter,
                self.payment_list,
                str(self.user.pk) if self.user else None,
            )
        )
        return self.payment_list

    def _update_purposes(self, purposes: list | None) -> None:
        if purposes is not None:
            self.payment_list.payment_plan_purposes.set(purposes)

    def _set_program_cycle(self, input_data: dict) -> None:
        if program_cycle_id := input_data.get("program_cycle_id"):
            program_cycle = get_object_or_404(
                ProgramCycle, pk=program_cycle_id, program=self.payment_list.program_cycle.program
            )
            if program_cycle == self.payment_list.program_cycle:
                return
            if self.payment_list.status != PaymentList.Status.TP_OPEN:
                raise ValidationError("Programme Cycle can be changed only within Open status")
            self._validate_pp_cycle(program_cycle)
            self.payment_list.program_cycle = program_cycle
            if not (payment_plan_id := input_data.get("payment_plan_id")):
                raise ValidationError("Payment Plan is required when changing Programme Cycle.")
            payment_plan = (
                PaymentPlan.objects.select_for_update().filter(pk=payment_plan_id, cycle=program_cycle).first()
            )
            if payment_plan is None:
                raise ValidationError("Payment Plan does not exist in the given Programme Cycle.")
            self._move_to_payment_plan(payment_plan)

    def _set_payment_plan_for_open_payment_list(self, input_data: dict) -> None:
        """Allow reassigning the payment plan on an open payment list without changing its cycle."""
        if self.payment_list.status != PaymentList.Status.TP_OPEN:
            return
        payment_plan_id = input_data.get("payment_plan_id")
        if not payment_plan_id:
            return
        # Skip: cycle is changing, _set_program_cycle already handles the payment plan in that case
        new_cycle_id = input_data.get("program_cycle_id")
        if new_cycle_id and new_cycle_id != self.payment_list.program_cycle_id:
            return
        payment_plan = (
            PaymentPlan.objects.select_for_update()
            .filter(pk=payment_plan_id, cycle=self.payment_list.program_cycle)
            .first()
        )
        if payment_plan is None:
            raise ValidationError("Payment Plan does not exist in the given Programme Cycle.")
        self._move_to_payment_plan(payment_plan)

    def _move_to_payment_plan(self, payment_plan: PaymentPlan) -> None:
        """Put the plan in the payment plan; it takes the payment plan's FSP now and its currency when it is opened."""
        self._validate_payment_plan_accepts_new_payment_lists(payment_plan)
        currency = payment_plan.currency
        delivery_mechanism = self.payment_list.delivery_mechanism
        if currency is not None and delivery_mechanism is not None:
            self.validate_currency_for_delivery_mechanism(currency, delivery_mechanism)
        self.payment_list.payment_plan = payment_plan

    def _validate_pp_status(
        self,
        excluded_ids: Any,
        exclusion_reason: Any,
        input_data: dict,
        **kwargs: Any,
    ) -> None:
        rules = kwargs.get("rules")
        vulnerability_score_max = kwargs.get("vulnerability_score_max")
        vulnerability_score_min = kwargs.get("vulnerability_score_min")
        if any([excluded_ids, exclusion_reason, rules]) and not self.payment_list.is_population_open():
            raise ValidationError(f"Not Allow edit targeting criteria within status {self.payment_list.status}")

        if not self.payment_list.is_population_locked() and (vulnerability_score_min or vulnerability_score_max):
            raise ValidationError(
                "You can only set vulnerability_score_min and vulnerability_score_max on Locked Population status"
            )

    @staticmethod
    def validate_currency_for_delivery_mechanism(currency: Currency, delivery_mechanism: DeliveryMechanism) -> None:
        is_digital = delivery_mechanism.transfer_type == DeliveryMechanism.TransferType.DIGITAL.value
        if (currency.code == "USDC") != is_digital:
            raise ValidationError(
                "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
            )

    def _set_additional_flags_for_tp(self, input_data: dict, targeting_criteria_input: dict) -> None:
        if "flag_exclude_if_on_sanction_list" in input_data:
            targeting_criteria_input["flag_exclude_if_on_sanction_list"] = input_data[
                "flag_exclude_if_on_sanction_list"
            ]
        if "flag_exclude_if_active_adjudication_ticket" in input_data:
            targeting_criteria_input["flag_exclude_if_active_adjudication_ticket"] = input_data[
                "flag_exclude_if_active_adjudication_ticket"
            ]

    @staticmethod
    def _validate_payment_plan_accepts_new_payment_lists(payment_plan: PaymentPlan) -> None:
        if payment_plan.source_payment_plan_id is not None:
            raise ValidationError(
                "Adding Target Population to a Follow-Up / Top-Up / Amendment Payment Plan is not possible"
            )
        if payment_plan.status != PaymentPlan.Status.OPEN:
            raise ValidationError(
                f"Adding Target Population to Payment Plan is possible only within Status {PaymentPlan.Status.OPEN}"
            )

    def _validate_pp_cycle(self, program_cycle: ProgramCycle) -> None:
        if program_cycle.status == ProgramCycle.FINISHED:
            raise ValidationError("Not possible to assign Finished Program Cycle")

    def _validate_pp_name(self, name: str, program: Program) -> str:
        if self.payment_list.status != PaymentList.Status.TP_OPEN:
            raise ValidationError("Name can be changed only within Open status")
        name = name.strip()

        if (
            PaymentList.objects.filter(name=name, program_cycle__program=program, is_removed=False)
            .exclude(id=self.payment_list.pk)
            .exists()
        ):
            raise ValidationError(f"Name '{name}' and program '{program.name}' already exists.")
        return name

    def delete(self) -> PaymentList:
        if self.payment_list.status not in [
            PaymentList.Status.OPEN,
            PaymentList.Status.TP_OPEN,
        ]:
            raise ValidationError("Deletion is only allowed when the status is 'Open'")

        if self.payment_list.plan_type != PaymentList.PlanType.REGULAR:
            return self._delete_child_plan()

        if self.payment_list.status == PaymentList.Status.OPEN:
            if self.payment_list.program_cycle.payment_lists.count() == 1:
                # if it's the last Payment Plan in this Cycle need to update Cycle status
                # move from Active to Draft Cycle need to delete all Payment Plans
                self.payment_list.program_cycle.set_draft()

            # with new proces just update status and not remove Payments and PaymentList
            flow = PaymentListFlow(self.payment_list)
            flow.status_draft()

        if self.payment_list.status == PaymentList.Status.TP_OPEN:
            self.payment_list.payment_items.all().delete()
            self.payment_list.delete()

        self.payment_list.save()

        return self.payment_list

    def _delete_child_plan(self) -> PaymentList:
        """Soft-delete the most recent child plan (Top-Up / Follow-Up / Amendment) together with its payments."""
        payment_list = self.payment_list
        if payment_list.has_newer_sibling_plan:
            raise ValidationError(
                f"Only the most recent {payment_list.get_plan_type_display()} of this Payment List can be deleted"
            )

        with transaction.atomic():
            # Take the same source-plan lock as prepare_child_payment_list_async_task_action,
            # so the delete cannot interleave with the async payment copy onto this plan.
            PaymentList.objects.select_for_update().get(pk=payment_list.source_payment_list_id)
            payment_list.payment_items.all().delete()
            payment_list.delete()
        return payment_list

    def export_xlsx(self, user_id: str) -> PaymentList:
        flow = PaymentListFlow(self.payment_list)
        flow.background_action_status_xlsx_exporting()
        self.payment_list.save(update_fields=["background_action_status"])

        create_payment_list_xlsx_async_task(payment_list=self.payment_list, user_id=str(user_id))
        self.payment_list.refresh_from_db(fields=["background_action_status", "export_file_entitlement"])
        return self.payment_list

    CHILD_PLAN_NAME_SUFFIX = {
        PaymentList.PlanType.FOLLOW_UP: " Follow Up",
        PaymentList.PlanType.TOP_UP: " Top Up",
        PaymentList.PlanType.TOP_UP_AMENDMENT: " Amendment",
    }

    def _create_child_payment_list(  # noqa: PLR0913
        self,
        user: Union["User", "AbstractBaseUser", "AnonymousUser"],
        plan_type: "PaymentList.PlanType",
        *,
        payment_plan: PaymentPlan | None,
        follow_up_instruction: "FollowUpInstruction | None" = None,
    ) -> PaymentList:
        """Create a child Payment Plan (follow-up / top-up / top-up amendment) of the current plan.

        Shared core for all three flows: the child inherits the source plan's purposes, dates and
        delivery mechanism and is created OPEN, in the linked payment plan it was created for or, for a
        Follow-Up Instruction child, under the instruction with no payment plan. Its dispersion dates and payment
        gateway flag are the linked payment plan's or the instruction's.
        """
        source_pp = self.payment_list
        child_pp = PaymentList.objects.create(
            name=source_pp.name + self.CHILD_PLAN_NAME_SUFFIX[plan_type],  # type: ignore[operator]
            status=PaymentList.Status.OPEN,
            build_status=PaymentList.BuildStatus.BUILD_STATUS_OK,
            built_at=timezone.now(),
            status_date=timezone.now(),
            plan_type=plan_type,
            source_payment_list=source_pp,
            business_area=source_pp.business_area,
            created_by=user,
            program_cycle=source_pp.program_cycle,
            start_date=source_pp.start_date,
            end_date=source_pp.end_date,
            delivery_mechanism=source_pp.delivery_mechanism,
            payment_plan=payment_plan,
            follow_up_instruction=follow_up_instruction,
        )
        self.copy_target_criteria(source_pp, child_pp)
        child_pp.payment_plan_purposes.set(source_pp.payment_plan_purposes.all())
        return child_pp

    def _copy_payments(
        self,
        source_payments: "QuerySet[Payment]",
        *,
        copy_entitlement: bool,
        is_follow_up: bool,
        amounts: dict[str, Decimal] | None = None,
    ) -> None:
        """Copy the given source payments into this child plan.

        Shared core for all three flows. FollowUp copies the entitlement of each source payment;
        TopUp is handed ``amounts`` (source payment unicef_id -> amount) chosen by the operator at
        creation time; TopUp amendment leaves the entitlement empty (``None``) for the operator to
        set later with the standard entitlement tools.
        """
        if self.payment_list.payment_items.exists():
            # Re-entry guard: the async copy job can be redelivered after a successful
            # commit (acks_late). If payments already exist, the copy ran — skip it
            # instead of hitting the payment_plan_and_household unique constraint.
            return

        exchange_rate_owner = self.payment_list.exchange_rate_owner
        if exchange_rate_owner is None:
            raise ValidationError("A payment list needs a payment plan or Follow-Up Instruction for its exchange rate.")
        if exchange_rate_owner.exchange_rate is None:
            exchange_rate_owner.exchange_rate = self.payment_list.get_exchange_rate()
            exchange_rate_owner.save(update_fields=["exchange_rate", "updated_at"])

        if not (split := self.payment_list.splits.first()):
            split = PaymentListSplit.objects.create(payment_list=self.payment_list)

        exchange_rate = Decimal(self.payment_list.exchange_rate or 0)
        # Without a rate on the plan, get_quantity_in_usd builds its own ExchangeRates — a full
        # rates fetch and parse — on every single call, so hand it one built up front.
        exchange_rates_client = ExchangeRates() if amounts and not exchange_rate else None

        def entitlement_of(payment: Payment) -> tuple[Decimal | None, Decimal | None]:
            if amounts is not None:
                quantity = amounts[cast("str", payment.unicef_id)]
                return quantity, get_quantity_in_usd(
                    amount=quantity,
                    currency=self.payment_list.currency,
                    exchange_rate=exchange_rate,
                    currency_exchange_date=self.payment_list.currency_exchange_date,
                    exchange_rates_client=exchange_rates_client,
                )
            if copy_entitlement:
                return payment.entitlement_quantity, payment.entitlement_quantity_usd
            return None, None

        copied_payments = []
        for payment in source_payments:
            entitlement_quantity, entitlement_quantity_usd = entitlement_of(payment)
            copied_payments.append(
                Payment(
                    parent=self.payment_list,
                    parent_split=split,
                    source_payment=payment,
                    program_id=self.payment_list.program_cycle.program_id,
                    is_follow_up=is_follow_up,
                    business_area_id=payment.business_area_id,
                    status=Payment.STATUS_PENDING,
                    status_date=timezone.now(),
                    household_id=payment.household_id,
                    head_of_household_id=payment.head_of_household_id,
                    collector_id=payment.collector_id,
                    collector_type=payment.collector_type,
                    currency_id=payment.currency_id,
                    entitlement_quantity=entitlement_quantity,
                    entitlement_quantity_usd=entitlement_quantity_usd,
                    entitlement_date=timezone.now() if amounts is not None else None,
                    financial_service_provider=self.payment_list.financial_service_provider,
                    delivery_type=self.payment_list.delivery_mechanism,
                )
            )
        Payment.objects.bulk_create(copied_payments)
        create_payment_list_snapshot_data(self.payment_list)
        PaymentListService.generate_signature(self.payment_list)

    def create_follow_up_payments(self) -> None:
        self._copy_payments(
            self.payment_list.source_payment_list.unsuccessful_payments_for_follow_up(),
            copy_entitlement=True,
            is_follow_up=True,
        )

    def create_funded_child_payments(
        self,
        amounts: dict[str, Decimal] | None = None,
        fixed_amount: Decimal | None = None,
    ) -> None:
        """Copy the funded slice of the source plan's eligible payments into this child plan.

        Shared by Top-Up and Top-Up Amendment: both are funded at creation the same way, and the
        source plan's type decides which pool they draw from.

        With ``fixed_amount`` every eligible beneficiary is copied and gets that amount. With
        ``amounts`` (from the uploaded template) only the beneficiaries listed there are copied —
        rows the operator left empty or at zero were dropped while parsing, and stay eligible for a
        later child plan.
        """
        eligible = self.payment_list.source_payment_list.eligible_payments_for_child_plan()
        if amounts is not None:
            eligible = eligible.filter(unicef_id__in=amounts.keys())
            # The pool is recomputed here, so a sibling plan created since the request may have
            # claimed some beneficiaries. Legitimate, but it must not shrink the plan silently.
            if missing := set(amounts) - set(eligible.values_list("unicef_id", flat=True)):
                logger.warning(
                    "Payment list %s: %d payment(s) from the amount file are no longer eligible "
                    "and will not be copied: %s",
                    self.payment_list.unicef_id,
                    len(missing),
                    sorted(missing),
                )
        elif fixed_amount is not None:
            amounts = {payment.unicef_id: fixed_amount for payment in eligible}
        self._copy_payments(eligible, copy_entitlement=False, is_follow_up=False, amounts=amounts)

    def create_child_plan_payments(
        self,
        amounts: dict[str, Decimal] | None = None,
        fixed_amount: Decimal | None = None,
    ) -> None:
        match self.payment_list.plan_type:
            case PaymentList.PlanType.FOLLOW_UP:
                self.create_follow_up_payments()
            case PaymentList.PlanType.TOP_UP | PaymentList.PlanType.TOP_UP_AMENDMENT:
                self.create_funded_child_payments(amounts=amounts, fixed_amount=fixed_amount)
            case _:
                raise ValidationError(f"Unsupported child payment list type: {self.payment_list.plan_type}")

    @transaction.atomic
    def create_follow_up(
        self,
        user: Union["User", "AbstractBaseUser", "AnonymousUser"],
        *,
        payment_plan: PaymentPlan | None = None,
        follow_up_instruction: "FollowUpInstruction | None" = None,
    ) -> PaymentList:
        """Create a Follow-Up of this payment list in a linked payment plan, or under its Follow-Up Instruction."""
        source_pp = self.payment_list

        if source_pp.plan_type == PaymentList.PlanType.FOLLOW_UP:
            raise ValidationError("Cannot create a follow-up of a follow-up Payment List")

        if not source_pp.unsuccessful_payments_for_follow_up().exists():
            raise ValidationError("Cannot create a follow-up for a payment list with no unsuccessful payments")

        follow_up_pp = self._create_child_payment_list(
            user,
            PaymentList.PlanType.FOLLOW_UP,
            payment_plan=payment_plan,
            follow_up_instruction=follow_up_instruction,
        )
        transaction.on_commit(lambda: prepare_child_payment_list_async_task(follow_up_pp))
        return follow_up_pp

    @transaction.atomic
    def create_top_up(  # noqa: PLR0913
        self,
        user: Union["User", "AbstractBaseUser", "AnonymousUser"],
        *,
        payment_plan: PaymentPlan,
        fixed_amount: Decimal | None = None,
        amounts: dict[str, Decimal] | None = None,
    ) -> PaymentList:
        """Create a Top-Up of this plan, funded either by a flat amount or per beneficiary.

        Exactly one of ``fixed_amount`` / ``amounts`` is expected; the request serializer enforces
        that. ``amounts`` already holds only the funded beneficiaries — parsing dropped the rows
        left empty or at zero.
        """
        source_pp = self.payment_list

        if source_pp.plan_type != PaymentList.PlanType.REGULAR:
            raise ValidationError(
                f"Top-up Payment List can only be created from a Standard payment list, got {source_pp.plan_type}"
            )

        if source_pp.status not in PaymentList.CHILD_PLAN_SOURCE_STATUSES:
            raise ValidationError(
                f"Top-up Payment List can only be created from an Accepted or Finished payment list, "
                f"got {source_pp.status}"
            )

        if not source_pp.eligible_payments_for_top_up().exists():
            raise ValidationError("Cannot create a top-up for a payment list with no eligible payments")

        top_up_pp = self._create_child_payment_list(
            user,
            PaymentList.PlanType.TOP_UP,
            payment_plan=payment_plan,
        )
        self._queue_child_payment_copy(top_up_pp, fixed_amount=fixed_amount, amounts=amounts)
        return top_up_pp

    @transaction.atomic
    def create_top_up_amendment(  # noqa: PLR0913
        self,
        user: Union["User", "AbstractBaseUser", "AnonymousUser"],
        *,
        payment_plan: PaymentPlan,
        fixed_amount: Decimal | None = None,
        amounts: dict[str, Decimal] | None = None,
    ) -> PaymentList:
        """Create an Amendment of this Top-Up, funded exactly like the Top-Up itself was.

        Same dialog, same two ways to fund it; the only difference is that the source is a Top-Up
        rather than a Standard plan.
        """
        source_pp = self.payment_list

        if source_pp.plan_type != PaymentList.PlanType.TOP_UP:
            raise ValidationError(
                f"Top-up Amendment can only be created from a Top Up payment list, got {source_pp.plan_type}"
            )

        if source_pp.status not in PaymentList.CHILD_PLAN_SOURCE_STATUSES:
            raise ValidationError(
                f"Top-up Amendment can only be created from an Accepted or Finished payment list, "
                f"got {source_pp.status}"
            )

        if not source_pp.eligible_payments_for_top_up_amendment().exists():
            raise ValidationError("Cannot create a top-up amendment for a payment list with no eligible payments")

        amendment_pp = self._create_child_payment_list(
            user,
            PaymentList.PlanType.TOP_UP_AMENDMENT,
            payment_plan=payment_plan,
        )
        self._queue_child_payment_copy(amendment_pp, fixed_amount=fixed_amount, amounts=amounts)
        return amendment_pp

    @staticmethod
    def _queue_child_payment_copy(
        child_pp: PaymentList,
        *,
        fixed_amount: Decimal | None,
        amounts: dict[str, Decimal] | None,
    ) -> None:
        """Hand the funding decision over to the async copy job.

        Amounts are stringified because the job config is JSON, and JSON has no decimal type —
        a float would round the money on the way through.
        """
        # Amounts ride in the job config (~40 B of jsonb per beneficiary) — no practical size limit.
        extra_config: dict[str, Any] = {}
        if amounts is not None:
            extra_config["amounts"] = {unicef_id: str(amount) for unicef_id, amount in amounts.items()}
        elif fixed_amount is not None:
            extra_config["fixed_amount"] = str(fixed_amount)
        transaction.on_commit(lambda: prepare_child_payment_list_async_task(child_pp, extra_config=extra_config))

    def create_child_plan(  # noqa: PLR0913
        self,
        *,
        plan_type: "PaymentList.PlanType",
        user: Union["User", "AbstractBaseUser", "AnonymousUser"],
        payment_plan: PaymentPlan,
        top_up_amount: "Decimal | dict[str, Decimal] | None" = None,
    ) -> PaymentList:
        """Create a child payment list of the requested type in ``payment_plan``.

        ``payment_plan`` is the linked payment plan of the source payment list.

        ``top_up_amount`` applies to Top-Ups and their Amendments: a ``Decimal`` funds every
        eligible beneficiary with that flat amount, a mapping of source payment unicef_id to
        amount funds exactly the beneficiaries it lists.
        """
        amounts = top_up_amount if isinstance(top_up_amount, dict) else None
        fixed_amount = top_up_amount if isinstance(top_up_amount, Decimal) else None
        match plan_type:
            case PaymentList.PlanType.FOLLOW_UP:
                return self.create_follow_up(user, payment_plan=payment_plan)
            case PaymentList.PlanType.TOP_UP:
                return self.create_top_up(
                    user,
                    payment_plan=payment_plan,
                    fixed_amount=fixed_amount,
                    amounts=amounts,
                )
            case PaymentList.PlanType.TOP_UP_AMENDMENT:
                return self.create_top_up_amendment(
                    user,
                    payment_plan=payment_plan,
                    fixed_amount=fixed_amount,
                    amounts=amounts,
                )
            case _:
                raise ValidationError(f"Unsupported child payment list type: {plan_type}")

    def recalculate_signatures_in_batch(self, batch_size: int = 500) -> None:
        payment_list = self.payment_list
        payments_ids = list(payment_list.eligible_payments.values_list("id", flat=True))
        for batch_start in range(0, len(payments_ids), batch_size):
            batched_ids = payments_ids[batch_start : batch_start + batch_size]
            payments = Payment.objects.filter(id__in=batched_ids).select_related(
                "household_snapshot", "currency", "delivery_type"
            )
            for payment in payments:
                payment.update_signature_hash()
            Payment.objects.bulk_update(payments, ("signature_hash",))

    def _build_payments_chunks(
        self, split_type: str, chunks_no: int | None, payments: Any, payments_count: int
    ) -> list:
        if split_type == PaymentListSplit.SplitType.BY_RECORDS:
            self._validate_split_by_record(chunks_no)
            return list(chunks(payments.order_by("unicef_id"), chunks_no))  # type: ignore[arg-type]

        if split_type in [
            PaymentListSplit.SplitType.BY_ADMIN_AREA1,
            PaymentListSplit.SplitType.BY_ADMIN_AREA2,
            PaymentListSplit.SplitType.BY_ADMIN_AREA3,
        ]:
            area_level = split_type[-1]
            grouped_payments = list(
                payments.order_by(f"household__admin{area_level}__p_code", "unicef_id").select_related(
                    f"household__admin{area_level}"
                )
            )
            return [
                list(g) for _, g in groupby(grouped_payments, key=lambda x: getattr(x.household, f"admin{area_level}"))
            ]

        if split_type == PaymentListSplit.SplitType.BY_COLLECTOR:
            grouped_payments = list(payments.order_by("collector__unicef_id", "unicef_id").select_related("collector"))
            return [list(g) for _, g in groupby(grouped_payments, key=lambda x: x.collector)]

        if split_type == PaymentListSplit.SplitType.NO_SPLIT:
            return [list(payments)]

        return []

    def _persist_splits(self, payments_chunks: list, split_type: str, chunks_no: int | None) -> None:
        if self.payment_list.splits.exists():
            self.payment_list.splits.all().delete()

        payment_list_splits_to_create = [
            PaymentListSplit(
                payment_list=self.payment_list,
                split_type=split_type,
                chunks_no=chunks_no,
                order=i,
            )
            for i in range(len(payments_chunks))
        ]
        PaymentListSplit.objects.bulk_create(payment_list_splits_to_create)
        for i, chunk in enumerate(payments_chunks):
            payment_list_splits_to_create[i].split_payment_items.set(chunk)

    def split(self, split_type: str, chunks_no: int | None = None) -> PaymentList:
        """Split the plan's payments into parts of the chosen shape.

        The payment plan picks one shape for every payment list in it, so "by records" with more records
        than the payment list has payments gives a single part rather than an error.
        """
        payments = self.payment_list.eligible_payments.all()
        payments_count = payments.count()
        if not payments_count:
            raise ValidationError("No payments to split")

        payments_chunks = self._build_payments_chunks(split_type, chunks_no, payments, payments_count)

        payments_chunks_count = len(payments_chunks)
        if payments_chunks_count > PaymentListSplit.MAX_CHUNKS:
            raise ValidationError(
                f"Too many Payment Parts to split: {payments_chunks_count}, maximum is {PaymentListSplit.MAX_CHUNKS}"
            )

        with transaction.atomic():
            self._persist_splits(payments_chunks, split_type, chunks_no)

        return self.payment_list

    def _validate_split_by_record(self, chunks_no: int | None) -> None:
        if not chunks_no:
            raise ValidationError("Payments Number is required for split by records")

        if chunks_no < PaymentListSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK:
            raise ValidationError(
                f"Payment Parts number should be at least {PaymentListSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK}"
            )

    def full_rebuild(self) -> None:
        payment_list: PaymentList = self.payment_list
        # remove all payment and recreate
        payment_list.payment_items(manager="all_objects").all().delete()

        self.create_payments(payment_list)

        payment_list.update_population_count_fields()

    @staticmethod
    def rebuild_payment_list_population(
        rebuild_list: bool,
        should_update_money_stats: bool,
        vulnerability_filter: bool,
        payment_list: PaymentList,
        user_id: str | None = None,
    ) -> None:
        from hope.apps.payment.celery_tasks import payment_list_apply_steficon_hh_selection_async_task

        rebuild_full_list = payment_list.status in PaymentList.PRE_PAYMENT_LIST_STATUSES and rebuild_list

        flow = PaymentListFlow(payment_list)
        flow.build_status_pending()
        payment_list.save(update_fields=("build_status", "built_at", "updated_at"))

        if rebuild_full_list:
            if vulnerability_filter and payment_list.steficon_rule_targeting:
                # in case of full rebuild and vulnerability filter, need to run steficon after rebuild
                payment_list_full_rebuild_async_task(payment_list)
                payment_list_apply_steficon_hh_selection_async_task(
                    payment_list, str(payment_list.steficon_rule_targeting.rule_id), user_id
                )
            elif should_update_money_stats:
                payment_list_full_rebuild_async_task(payment_list)
                payment_list_rebuild_stats_async_task(payment_list)
            else:
                payment_list_full_rebuild_async_task(payment_list)
            return

        if should_update_money_stats:
            payment_list_rebuild_stats_async_task(payment_list)

        if vulnerability_filter:
            params = {}
            if payment_list.vulnerability_score_max is not None:
                params["vulnerability_score__lte"] = payment_list.vulnerability_score_max
            if payment_list.vulnerability_score_min is not None:
                params["vulnerability_score__gte"] = payment_list.vulnerability_score_min
            payment_list.payment_items(manager="all_objects").filter(**params).update(is_removed=False)
            payment_list.payment_items(manager="all_objects").exclude(**params).update(is_removed=True)
            payment_list_rebuild_stats_async_task(payment_list)

    @staticmethod
    def copy_target_criteria(source_pp: PaymentList, target_pp: PaymentList) -> None:
        for rule in source_pp.get_rules():
            rule_copy = TargetingCriteriaRule(
                payment_list=target_pp,
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
                    targeting_criteria_rule=rule_copy,
                    target_only_hoh=ind_filter_block.target_only_hoh,
                )
                ind_filter_block_copy.save()
                for ind_filter in ind_filter_block.individual_block_filters.all():
                    ind_filter.pk = None
                    ind_filter.individuals_filters_block = ind_filter_block_copy
                    ind_filter.save()

    def ready_for_closure(self) -> PaymentList:
        with transaction.atomic():
            payment_list = PaymentList.objects.select_for_update().get(pk=self.payment_list.pk)
            if payment_list.status != PaymentList.Status.FINISHED:
                raise ValidationError(
                    f"Mark as Ready for Closure is possible only within Status {PaymentList.Status.FINISHED}"
                )
            flow = PaymentListFlow(payment_list)
            flow.status_ready_for_closure()
            payment_list.save(update_fields=("status", "status_date", "updated_at"))
            payment_list.refresh_from_db(fields=["status", "status_date", "updated_at"])

        self.payment_list = payment_list
        return self.payment_list

    def send_back_to_finished(self) -> PaymentList:
        with transaction.atomic():
            payment_list = PaymentList.objects.select_for_update().get(pk=self.payment_list.pk)
            if payment_list.status != PaymentList.Status.READY_FOR_CLOSURE:
                raise ValidationError(
                    f"Send Back is possible only within Status {PaymentList.Status.READY_FOR_CLOSURE}"
                )
            flow = PaymentListFlow(payment_list)
            flow.status_finished()
            payment_list.save(update_fields=("status", "status_date", "updated_at"))
            payment_list.refresh_from_db(fields=["status", "status_date", "updated_at"])

        self.payment_list = payment_list
        return self.payment_list

    def close(self, closure_comment: str | None = None, user_id: str | None = None) -> PaymentList:
        with transaction.atomic():
            payment_list = PaymentList.objects.select_for_update().get(pk=self.payment_list.pk)
            if payment_list.status != PaymentList.Status.READY_FOR_CLOSURE:
                raise ValidationError(
                    f"Close Payment List is possible only within Status {PaymentList.Status.READY_FOR_CLOSURE}"
                )
            has_verification = payment_list.payment_verification_plans.filter(responded_count__gt=0).exists()
            if not has_verification and not closure_comment:
                raise ValidationError("Closure comment is required when no payment verification was carried out.")
            flow = PaymentListFlow(payment_list)
            flow.status_close()
            payment_list.closure_comment = closure_comment
            payment_list.closed_by_id = user_id
            payment_list.save(update_fields=("status", "status_date", "closure_comment", "closed_by_id", "updated_at"))
            payment_list.refresh_from_db(
                fields=["status", "status_date", "closure_comment", "closed_by_id", "updated_at"]
            )

        self.payment_list = payment_list
        return self.payment_list

    def abort(self, abort_comment: str | None, user_id: str | None = None) -> PaymentList:
        allowed_statuses = [
            PaymentList.Status.LOCKED,
            PaymentList.Status.LOCKED_FSP,
            PaymentList.Status.IN_APPROVAL,
            PaymentList.Status.IN_AUTHORIZATION,
            PaymentList.Status.IN_REVIEW,
        ]

        if self.payment_list.status not in allowed_statuses:
            raise ValidationError(f"Abort Payment List is not possible within Status {self.payment_list.status}")
        flow = PaymentListFlow(self.payment_list)
        flow.status_abort()
        self.payment_list.abort_comment = abort_comment or ""
        self.payment_list.save(update_fields=("status", "status_date", "updated_at", "abort_comment"))
        self.payment_list.refresh_from_db(fields=["status", "status_date", "updated_at", "abort_comment"])
        return self.payment_list

    def reactivate_abort(self, user_id: str | None = None) -> PaymentList:
        if self.payment_list.status != PaymentList.Status.ABORTED:
            raise ValidationError(
                f"Reactivate Aborted Payment List is possible only within Status {PaymentList.Status.ABORTED}"
            )
        # Child plans take their collectors and entitlements from the source plan, so only regular plans are refreshed.
        if self.payment_list.plan_type == PaymentList.PlanType.REGULAR:
            return self._queue_reactivate_rebuild(user_id)

        flow = PaymentListFlow(self.payment_list)
        flow.status_reactivate_abort()
        self.payment_list.save(update_fields=("status", "status_date", "updated_at"))
        self.payment_list.refresh_from_db(fields=["status", "status_date", "updated_at"])
        # An aborted plan was locked, so its payments still carry the lock's conflict flags.
        self.clear_lock_conflicts()
        self.payment_list.update_population_count_fields()
        self.payment_list.update_money_fields()
        return self.payment_list

    def _queue_reactivate_rebuild(self, user_id: str | None) -> PaymentList:
        """Queue the payees refresh; the plan stays ABORTED until the task has rebuilt it."""
        background_action_status = self.payment_list.background_action_status
        if (
            background_action_status is not None
            and background_action_status not in PaymentList.BACKGROUND_ACTION_ERROR_STATES
        ):
            raise ValidationError("Another background action is already in progress.")
        flow = PaymentListFlow(self.payment_list)
        flow.background_action_status_rebuilding()
        flow.build_status_pending()
        self.payment_list.save(update_fields=("background_action_status", "build_status", "built_at", "updated_at"))
        transaction.on_commit(lambda: payment_list_refresh_payees_async_task(self.payment_list, user_id))
        return self.payment_list

    def refresh_payees(self) -> None:
        """Bring the payments of a reactivated plan up to date without changing the targeted population.

        Collectors, wallet validity and household snapshots are resolved again from the current household data.
        Entitlements and conflicts are cleared because the plan goes through locking and entitlement setup again.
        """
        payment_list = self.payment_list
        payments = list(payment_list.payment_items(manager="all_objects").all())
        payments_by_household_id = {payment.household_id: payment for payment in payments}
        household_rows, collectors_by_id, wallet_validity_by_collector_id = self._resolve_collectors(
            payment_list, Household.objects.filter(id__in=payments_by_household_id.keys())
        )
        now = timezone.now()
        for payment in payments:
            payment.conflicted = False
            payment.entitlement_quantity = None
            payment.entitlement_quantity_usd = None
            payment.entitlement_date = None
        for household in household_rows:
            payment = payments_by_household_id[household["pk"]]
            collector, collector_type = self._get_collector(household, collectors_by_id)
            has_valid_wallet = wallet_validity_by_collector_id[collector.id]
            payment.collector = collector
            payment.collector_type = collector_type
            payment.head_of_household_id = household["head_of_household"]
            payment.has_valid_wallet = has_valid_wallet
            payment.status = (
                Payment.STATUS_PENDING if has_valid_wallet and not payment.excluded else Payment.STATUS_NOT_ELIGIBLE
            )
            payment.status_date = now
        Payment.all_objects.bulk_update(
            payments,
            [
                "conflicted",
                "entitlement_quantity",
                "entitlement_quantity_usd",
                "entitlement_date",
                "collector",
                "collector_type",
                "head_of_household",
                "has_valid_wallet",
                "status",
                "status_date",
            ],
            batch_size=500,
        )
        PaymentHouseholdSnapshot.objects.filter(payment__parent=payment_list).delete()
        create_payment_list_snapshot_data(payment_list)
        payment_list.update_money_fields()

    @classmethod
    def send_reconciliation_overdue_emails(cls) -> None:
        today = datetime.date.today()

        overdue_payment_lists = (
            PaymentList.objects.annotate(
                due_date=ExpressionWrapper(
                    Coalesce(
                        F("payment_plan__dispersion_start_date"),
                        F("follow_up_instruction__dispersion_start_date"),
                    )
                    + F("program_cycle__program__reconciliation_window_in_days") * datetime.timedelta(days=1),
                    output_field=DateField(),
                )
            )
            .filter(
                status=PaymentList.Status.ACCEPTED,
                due_date=today,
                program_cycle__program__send_reconciliation_window_expiry_notifications=True,
                program_cycle__program__reconciliation_window_in_days__gte=1,
            )
            .distinct()
        )

        for pp in overdue_payment_lists:
            if pp.has_payments_reconciliation_overdue:
                send_payment_list_reconciliation_overdue_email_async_task(pp)

    def send_reconciliation_overdue_email_for_pp(self) -> None:
        users = users_with_permissions(
            self.payment_list.business_area,
            [Permissions.RECEIVE_PP_OVERDUE_EMAIL],
            [self.payment_list.program],
        )

        if users:
            text_template = "payment/payment_list_reconciliation_overdue_email.txt"
            html_template = "payment/payment_list_reconciliation_overdue_email.html"

            payment_list_id = str(self.payment_list.id)
            program_code = self.payment_list.program.code
            payment_list_link = get_link(
                f"/{self.payment_list.business_area.slug}/programs/{program_code}/payment-module/payment-lists/{payment_list_id}"
            )

        for user in users:
            context = {
                "first_name": getattr(user, "first_name", "") or getattr(user, "username", ""),
                "last_name": getattr(user, "last_name", ""),
                "email": getattr(user, "email", ""),
                "message": f"Please be informed that Payment List: {self.payment_list.unicef_id} has exceeded its"
                f" reconciliation window of {self.payment_list.program.reconciliation_window_in_days} days."
                f" Please take the necessary steps to complete the reconciliation process timely.",
                "title": f"Payment List {self.payment_list.unicef_id} Reconciliation Overdue",
                "link": payment_list_link,
            }

            user.email_user(
                subject=context["title"],
                html_body=render_to_string(html_template, context=context),
                text_body=render_to_string(text_template, context=context),
            )
