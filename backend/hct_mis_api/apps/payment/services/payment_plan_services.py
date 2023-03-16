import logging
from decimal import Decimal
from functools import partial
from typing import IO, TYPE_CHECKING, Callable, Dict, List, Optional

from django.contrib.admin.options import get_content_type_for_model
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from constance import config
from graphql import GraphQLError
from psycopg2._psycopg import IntegrityError

from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.celery_tasks import (
    create_payment_plan_payment_list_xlsx,
    create_payment_plan_payment_list_xlsx_per_fsp,
    import_payment_plan_payment_list_per_fsp_from_xlsx,
)
from hct_mis_api.apps.payment.models import (
    Approval,
    ApprovalProcess,
    Payment,
    PaymentPlan,
)
from hct_mis_api.apps.targeting.models import TargetPopulation

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User


class PaymentPlanService:
    def __init__(self, payment_plan: "PaymentPlan"):
        self.payment_plan = payment_plan

        self.action: Optional[str] = None
        self.user: Optional["User"] = None
        self.input_data: Optional[Dict] = None

    @property
    def actions_map(self) -> Dict:
        return {
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

    def execute_update_status_action(self, input_data: Dict, user: "User") -> PaymentPlan:
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
        actions = self.actions_map.keys()
        if self.action not in actions:
            raise GraphQLError(f"Not Implemented Action: {self.action}. List of possible actions: {actions}")

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
        return self.payment_plan

    def lock(self) -> PaymentPlan:
        if not self.payment_plan.can_be_locked:
            raise GraphQLError("At least one valid Payment should exist in order to Lock the Payment Plan")

        self.payment_plan.payment_items.all().filter(payment_plan_hard_conflicted=True).update(excluded=True)
        self.payment_plan.status_lock()
        self.payment_plan.update_population_count_fields()
        self.payment_plan.update_money_fields()

        self.payment_plan.save()

        return self.payment_plan

    def unlock(self) -> PaymentPlan:
        self.payment_plan.delivery_mechanisms.all().delete()
        self.payment_plan.status_unlock()
        self.payment_plan.update_population_count_fields()
        self.payment_plan.update_money_fields()
        self.payment_plan.remove_export_file()

        self.payment_plan.save()

        return self.payment_plan

    def lock_fsp(self) -> PaymentPlan:
        if self.payment_plan.delivery_mechanisms.filter(
            Q(financial_service_provider__isnull=True) | Q(delivery_mechanism__isnull=True)
        ).exists():
            msg = "There are no Delivery Mechanisms / FSPs chosen for Payment Plan"
            logging.exception(msg)
            raise GraphQLError(msg)

        dm_to_fsp_mapping = [
            {
                "fsp": delivery_mechanism_per_payment_plan.financial_service_provider,
                "delivery_mechanism_per_payment_plan": delivery_mechanism_per_payment_plan,
            }
            for delivery_mechanism_per_payment_plan in self.payment_plan.delivery_mechanisms.all().order_by(
                "delivery_mechanism_order"
            )
        ]
        self.validate_fsps_per_delivery_mechanisms(dm_to_fsp_mapping, update_dms=False, update_payments=True)

        self.payment_plan.status_lock_fsp()
        self.payment_plan.save()

        return self.payment_plan

    def unlock_fsp(self) -> Optional[PaymentPlan]:
        self.payment_plan.status_unlock_fsp()
        self.payment_plan.payment_items.all().update(financial_service_provider=None, delivery_type=None)
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
            raise GraphQLError(msg)

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
            raise GraphQLError(
                f"Not possible to create {self.action} for Payment Plan within status {self.payment_plan.status}"
            )

    def validate_acceptance_process_approval_count(self, approval_process: ApprovalProcess) -> None:
        approval_type = self.get_approval_type_by_action()
        required_number = self.get_required_number_by_approval_type(approval_process)
        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            raise GraphQLError(
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
                    raise GraphQLError(
                        f"Can't create {approval_type}. User have already created {created_approval_type}"
                    )
            # validate other approval types
            elif approvals_by_user.filter(type=approval_type).exists():
                raise GraphQLError(f"Can't create new {approval_type}. User have already created {approval_type}")

    def check_payment_plan_and_update_status(self, approval_process: ApprovalProcess) -> None:
        approval_type = self.get_approval_type_by_action()
        required_number = self.get_required_number_by_approval_type(approval_process)

        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            if approval_type == Approval.APPROVAL:
                self.payment_plan.status_approve()
                approval_process.sent_for_authorization_by = self.user
                approval_process.sent_for_authorization_date = timezone.now()
                approval_process.save()

            if approval_type == Approval.AUTHORIZATION:
                self.payment_plan.status_authorize()
                approval_process.sent_for_finance_release_by = self.user
                approval_process.sent_for_finance_release_date = timezone.now()
                approval_process.save()

            if approval_type == Approval.FINANCE_RELEASE:
                self.payment_plan.status_mark_as_reviewed()
                # remove imported and export files

            if approval_type == Approval.REJECT:
                self.payment_plan.status_reject()

            self.payment_plan.save()

    @staticmethod
    def _create_payments(payment_plan: PaymentPlan) -> None:
        payments_to_create = []
        for household in payment_plan.target_population.households.all():
            try:
                collector = household.individuals_and_roles.filter(role=ROLE_PRIMARY).first().individual
            except AttributeError as exception:
                msg = f"Couldn't find a primary collector in {household}"
                logging.exception(msg)
                raise GraphQLError(msg) from exception

            payments_to_create.append(
                Payment(
                    parent=payment_plan,
                    business_area=payment_plan.business_area,
                    status=Payment.STATUS_PENDING,
                    status_date=timezone.now(),
                    household=household,
                    head_of_household=household.head_of_household,
                    collector=collector,
                    currency=payment_plan.currency,
                )
            )
        try:
            Payment.objects.bulk_create(payments_to_create)
        except IntegrityError:
            raise GraphQLError("Duplicated Households in provided Targeting")

    @staticmethod
    def create(input_data: Dict, user: "User") -> PaymentPlan:
        business_area = BusinessArea.objects.get(slug=input_data["business_area_slug"])
        if not business_area.is_payment_plan_applicable:
            raise GraphQLError("PaymentPlan can not be created in provided Business Area")

        targeting_id = decode_id_string(input_data["targeting_id"])
        try:
            target_population = TargetPopulation.objects.get(
                id=targeting_id, status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
            )
        except TargetPopulation.DoesNotExist:
            raise GraphQLError(
                f"TargetPopulation id:{targeting_id} does not exist or is not in status 'Ready for Payment Module'"
            )
        if not target_population.program:
            raise GraphQLError("TargetPopulation should have related Program defined")

        dispersion_end_date = input_data["dispersion_end_date"]
        if not dispersion_end_date or dispersion_end_date <= timezone.now().date():
            raise GraphQLError(f"Dispersion End Date [{dispersion_end_date}] cannot be a past date")

        start_date = input_data["start_date"]
        if start_date < target_population.program.start_date:
            raise GraphQLError("Start date cannot be earlier than start date in the program")

        end_date = input_data["end_date"]
        if end_date > target_population.program.end_date:
            raise GraphQLError("End date cannot be later that end date in the program")

        payment_plan = PaymentPlan.objects.create(
            business_area=business_area,
            created_by=user,
            target_population=target_population,
            program=target_population.program,
            currency=input_data["currency"],
            dispersion_start_date=input_data["dispersion_start_date"],
            dispersion_end_date=dispersion_end_date,
            status_date=timezone.now(),
            start_date=start_date,
            end_date=end_date,
        )

        PaymentPlanService._create_payments(payment_plan)
        payment_plan.refresh_from_db()
        payment_plan.update_population_count_fields()
        payment_plan.update_money_fields()

        payment_plan.target_population.status = TargetPopulation.STATUS_ASSIGNED
        payment_plan.target_population.save()

        return payment_plan

    def update(self, input_data: Dict) -> PaymentPlan:
        if self.payment_plan.status != PaymentPlan.Status.OPEN:
            raise GraphQLError("Only Payment Plan in Open status can be edited")

        recreate_payments = False
        recalculate_payments = False

        basic_fields = ["start_date", "end_date", "dispersion_start_date"]

        for basic_field in basic_fields:
            if basic_field in input_data and input_data[basic_field] != getattr(self.payment_plan, basic_field):
                setattr(self.payment_plan, basic_field, input_data[basic_field])

        targeting_id = decode_id_string(input_data.get("targeting_id"))
        if targeting_id and targeting_id != str(self.payment_plan.target_population.id):
            try:
                new_target_population = TargetPopulation.objects.get(
                    id=targeting_id, status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
                )

                if not new_target_population.program:
                    raise GraphQLError("TargetPopulation should have related Program defined")

                self.payment_plan.target_population.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
                self.payment_plan.target_population.save()

                self.payment_plan.target_population = new_target_population
                self.payment_plan.program = new_target_population.program
                self.payment_plan.target_population.status = TargetPopulation.STATUS_ASSIGNED
                self.payment_plan.target_population.save()
                recreate_payments = True
                recalculate_payments = True

            except TargetPopulation.DoesNotExist:
                raise GraphQLError(f"TargetPopulation id:{targeting_id} does not exist or is not in status Ready")

        if (
            input_data.get("dispersion_end_date")
            and input_data["dispersion_end_date"] != self.payment_plan.dispersion_end_date
        ):
            if input_data["dispersion_end_date"] <= timezone.now().date():
                raise GraphQLError(f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date")
            self.payment_plan.dispersion_end_date = input_data["dispersion_end_date"]
            recalculate_payments = True

        if input_data.get("currency") and input_data["currency"] != self.payment_plan.currency:
            self.payment_plan.currency = input_data["currency"]
            recreate_payments = True
            recalculate_payments = True

        if (
            input_data.get("start_date")
            and input_data["start_date"] < self.payment_plan.target_population.program.start_date
        ):
            raise GraphQLError("Start date cannot be earlier than start date in the program")

        if input_data.get("end_date") and input_data["end_date"] > self.payment_plan.target_population.program.end_date:
            raise GraphQLError("End date cannot be later that end date in the program")

        self.payment_plan.save()

        if recreate_payments:
            self.payment_plan.payment_items.all().delete()
            self._create_payments(self.payment_plan)

        if recalculate_payments:
            self.payment_plan.refresh_from_db()
            self.payment_plan.update_population_count_fields()
            self.payment_plan.update_money_fields()

        return self.payment_plan

    def delete(self) -> PaymentPlan:
        if self.payment_plan.status != PaymentPlan.Status.OPEN:
            raise GraphQLError("Only Payment Plan in Open status can be deleted")

        self.payment_plan.target_population.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
        self.payment_plan.target_population.save()
        self.payment_plan.delete()
        return self.payment_plan

    def export_xlsx(self, user: "User") -> PaymentPlan:
        self.payment_plan.background_action_status_xlsx_exporting()
        self.payment_plan.save()

        create_payment_plan_payment_list_xlsx.delay(self.payment_plan.pk, user.pk)
        return self.payment_plan

    def export_xlsx_per_fsp(self, user: "User") -> PaymentPlan:
        self.payment_plan.background_action_status_xlsx_exporting()
        self.payment_plan.save()

        create_payment_plan_payment_list_xlsx_per_fsp.delay(self.payment_plan.pk, user.pk)
        return self.payment_plan

    def import_xlsx_per_fsp(self, user: "User", file: IO) -> PaymentPlan:
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

    def validate_fsps_per_delivery_mechanisms(
        self, dm_to_fsp_mapping: List[Dict], update_dms: bool = False, update_payments: bool = False
    ) -> None:
        processed_payments = []
        with transaction.atomic():
            for mapping in dm_to_fsp_mapping:
                delivery_mechanism_per_payment_plan = mapping["delivery_mechanism_per_payment_plan"]
                delivery_mechanism = delivery_mechanism_per_payment_plan.delivery_mechanism
                fsp = mapping["fsp"]

                if delivery_mechanism_per_payment_plan.delivery_mechanism not in fsp.delivery_mechanisms:
                    raise GraphQLError(
                        f"Delivery mechanism '{delivery_mechanism_per_payment_plan.delivery_mechanism}' is not supported "
                        f"by FSP '{fsp}'"
                    )
                if not fsp.can_accept_any_volume():
                    raise GraphQLError(f"{fsp} cannot accept any volume")

                payments_for_delivery_mechanism = (
                    self.payment_plan.not_excluded_payments.exclude(
                        id__in=[processed_payment.id for processed_payment in processed_payments]
                    )
                    .distinct()
                    .order_by("unicef_id")
                )

                total_volume_for_delivery_mechanism = payments_for_delivery_mechanism.aggregate(
                    entitlement_quantity_usd__sum=Coalesce(Sum("entitlement_quantity_usd"), Decimal(0.0))
                )["entitlement_quantity_usd__sum"]
                if fsp.can_accept_volume(total_volume_for_delivery_mechanism):
                    processed_payments += list(payments_for_delivery_mechanism)
                    if update_payments:
                        payments_for_delivery_mechanism.update(
                            financial_service_provider=fsp,
                            delivery_type=delivery_mechanism,
                        )
                else:
                    # Process part of the volume up to the distribution limit
                    partial_processed_payments = []
                    partial_total_volume = Decimal(0.0)

                    for payment in payments_for_delivery_mechanism:
                        if fsp.distribution_limit < (partial_total_volume + payment.entitlement_quantity_usd):
                            break
                        partial_total_volume += payment.entitlement_quantity_usd
                        partial_processed_payments.append(payment)

                    processed_payments += partial_processed_payments
                    if update_payments:
                        for payment in partial_processed_payments:
                            payment.financial_service_provider = fsp
                            payment.delivery_type = delivery_mechanism
                            payment.save()
                if update_dms:
                    delivery_mechanism_per_payment_plan.financial_service_provider = fsp
                    delivery_mechanism_per_payment_plan.save()

            if set(processed_payments) != set(self.payment_plan.not_excluded_payments):
                raise GraphQLError("Some Payments were not assigned to selected DeliveryMechanisms/FSPs")
