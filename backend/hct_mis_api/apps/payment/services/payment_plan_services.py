import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from graphql import GraphQLError
from psycopg2._psycopg import IntegrityError

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    decode_id_string,
)
from hct_mis_api.apps.payment.models import PaymentPlan, Approval, ApprovalProcess, Payment
from hct_mis_api.apps.payment.celery_tasks import (
    create_payment_plan_payment_list_xlsx,
    create_payment_plan_payment_list_xlsx_per_fsp,
    import_payment_plan_payment_list_per_fsp_from_xlsx,
)
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.household.models import ROLE_PRIMARY


User = get_user_model()


class PaymentPlanService:
    def __init__(self, payment_plan=None):
        self.payment_plan = payment_plan

        self.action = None
        self.user = None
        self.input_data = None

    @property
    def actions_map(self) -> dict:
        return {
            PaymentPlan.Action.LOCK.value: self.lock,
            PaymentPlan.Action.LOCK_FSP.value: self.lock_fsp,
            PaymentPlan.Action.UNLOCK.value: self.unlock,
            PaymentPlan.Action.UNLOCK_FSP.value: self.unlock_fsp,
            PaymentPlan.Action.SEND_FOR_APPROVAL.value: self.send_for_approval,
            # use the same method for Approve, Authorize, Finance Review and Reject
            PaymentPlan.Action.APPROVE.value: self.acceptance_process,
            PaymentPlan.Action.AUTHORIZE.value: self.acceptance_process,
            PaymentPlan.Action.REVIEW.value: self.acceptance_process,
            PaymentPlan.Action.REJECT.value: self.acceptance_process,
        }

    def get_business_area_required_number_by_approval_type(self):
        business_area = self.payment_plan.business_area
        approval_count_map = {
            Approval.APPROVAL: business_area.approval_number_required,
            Approval.AUTHORIZATION: business_area.authorization_number_required,
            Approval.FINANCE_REVIEW: business_area.finance_review_number_required,
            Approval.REJECT: 1,  # be default only one Reject per Acceptance Process object
        }
        return approval_count_map.get(self.get_approval_type_by_action())

    def get_approval_type_by_action(self):
        actions_to_approval_type_map = {
            PaymentPlan.Action.APPROVE.value: Approval.APPROVAL,
            PaymentPlan.Action.AUTHORIZE.value: Approval.AUTHORIZATION,
            PaymentPlan.Action.REVIEW.value: Approval.FINANCE_REVIEW,
            PaymentPlan.Action.REJECT.value: Approval.REJECT,
        }
        return actions_to_approval_type_map.get(self.action)

    def execute_update_status_action(self, input_data: dict, user: User) -> PaymentPlan:
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

    def validate_action(self):
        actions = self.actions_map.keys()
        if self.action not in actions:
            raise GraphQLError(f"Not Implemented Action: {self.action}. List of possible actions: {actions}")

    def get_action_function(self):
        return self.actions_map.get(self.action)

    def send_for_approval(self):
        self.payment_plan.status_send_to_approval()
        self.payment_plan.save()
        # create new ApprovalProcess
        ApprovalProcess.objects.create(
            payment_plan=self.payment_plan, sent_for_approval_by=self.user, sent_for_approval_date=timezone.now()
        )
        return self.payment_plan

    def lock(self):
        if not self.payment_plan.can_be_locked:
            raise GraphQLError("At least one valid Payment should exist in order to Lock the Payment Plan")

        self.payment_plan.payment_items.all().filter(payment_plan_hard_conflicted=True).update(excluded=True)
        self.payment_plan.status_lock()
        self.payment_plan.update_population_count_fields()
        self.payment_plan.update_money_fields()

        self.payment_plan.save()

        return self.payment_plan

    def unlock(self):
        # TODO: clear FSP
        # TODO: clear entitlements

        self.payment_plan.payment_items.all().update(excluded=False)
        self.payment_plan.status_unlock()
        self.payment_plan.update_population_count_fields()
        self.payment_plan.update_money_fields()

        self.payment_plan.save()

        return self.payment_plan

    def lock_fsp(self):
        # TODO: cant lock FSP if no FSP choices

        # set all payments with money expected to be delivered

        self.payment_plan.status_lock_fsp()
        self.payment_plan.save()

        return self.payment_plan

    def unlock_fsp(self):
        self.payment_plan.status_unlock_fsp()
        self.payment_plan.save()

        return self.payment_plan

    def acceptance_process(self):
        self.validate_payment_plan_status_to_acceptance_process_approval_type()

        # every time we will create Approval for first created AcceptanceProcess
        # init creation AcceptanceProcess added in send_for_approval()
        approval_process = self.payment_plan.approval_process.first()
        if not approval_process:
            logging.exception(f"Approval Process object not found for PaymentPlan {self.payment_plan.pk}")
            raise GraphQLError(f"Approval Process object not found for PaymentPlan {self.payment_plan.pk}")

        # validate approval required number
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

    def validate_payment_plan_status_to_acceptance_process_approval_type(self):
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
        if self.payment_plan.status not in action_to_statuses_map.get(self.action):
            raise GraphQLError(
                f"Not possible to create {self.action} for Payment Plan within status {self.payment_plan.status}"
            )

    def validate_acceptance_process_approval_count(self, acceptance_process):
        approval_type = self.get_approval_type_by_action()
        required_number = self.get_business_area_required_number_by_approval_type()
        if acceptance_process.approvals.filter(type=approval_type).count() >= required_number:
            raise GraphQLError(
                f"Can't create new approval. Required Number ({required_number}) of {approval_type} is already created"
            )

    def check_payment_plan_and_update_status(self, approval_process):
        approval_type = self.get_approval_type_by_action()
        required_number = self.get_business_area_required_number_by_approval_type()

        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            if approval_type == Approval.APPROVAL:
                self.payment_plan.status_approve()
                approval_process.sent_for_authorization_by = self.user
                approval_process.sent_for_authorization_date = timezone.now()
                approval_process.save()

            if approval_type == Approval.AUTHORIZATION:
                self.payment_plan.status_authorize()
                approval_process.sent_for_finance_review_by = self.user
                approval_process.sent_for_finance_review_date = timezone.now()
                approval_process.save()

            if approval_type == Approval.FINANCE_REVIEW:
                self.payment_plan.status_mark_as_reviewed()
                # remove imported and export files
                self.payment_plan.remove_export_file()
                self.payment_plan.remove_imported_file()

            if approval_type == Approval.REJECT:
                self.payment_plan.status_reject()

            self.payment_plan.save()

    def _create_payments(self, payment_plan: PaymentPlan):
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
                    status=Payment.STATUS_NOT_DISTRIBUTED,
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

    def create(self, input_data: dict, user: User) -> PaymentPlan:
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

        payment_plan = PaymentPlan.objects.create(
            business_area=business_area,
            created_by=user,
            target_population=target_population,
            program=target_population.program,
            currency=input_data["currency"],
            dispersion_start_date=input_data["dispersion_start_date"],
            dispersion_end_date=dispersion_end_date,
            status_date=timezone.now(),
            start_date=input_data["start_date"],
            end_date=input_data["end_date"],
        )

        self._create_payments(payment_plan)
        payment_plan.refresh_from_db()
        payment_plan.update_population_count_fields()
        payment_plan.update_money_fields()

        payment_plan.target_population.status = TargetPopulation.STATUS_ASSIGNED
        payment_plan.target_population.save()

        return payment_plan

    def update(self, input_data: dict) -> PaymentPlan:
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

    def export_xlsx(self, user: User) -> PaymentPlan:
        create_payment_plan_payment_list_xlsx.delay(self.payment_plan.pk, user.pk)
        return self.payment_plan

    def export_xlsx_per_fsp(self, user: User) -> PaymentPlan:
        create_payment_plan_payment_list_xlsx_per_fsp.delay(self.payment_plan.pk, user.pk)
        return self.payment_plan

    def import_xlsx_per_fsp(self, user, file) -> PaymentPlan:
        import_payment_plan_payment_list_per_fsp_from_xlsx.delay(self.payment_plan.pk, user.pk, file)
        return self.payment_plan
