import logging

from django.utils import timezone
from graphql import GraphQLError

from hct_mis_api.apps.payment.inputs import PaymentPlanActionType
from hct_mis_api.apps.payment.models import PaymentPlan, Approval, ApprovalProcess


class PaymentPlanServices:
    def __init__(self, payment_plan, info, input_data):
        self.payment_plan = payment_plan
        self.input_data = input_data
        self.action = input_data.get("action")
        self.user = info.context.user

    def get_actions_map(self):
        actions_map = {
            PaymentPlanActionType.LOCK.value: self.lock,
            PaymentPlanActionType.UNLOCK.value: self.unlock,
            PaymentPlanActionType.SEND_FOR_APPROVAL.value: self.send_for_approval,
            # use the same method for Approve, Authorize, Finance Review and Reject
            PaymentPlanActionType.APPROVE.value: self.acceptance_process,
            PaymentPlanActionType.AUTHORIZE.value: self.acceptance_process,
            PaymentPlanActionType.REVIEW.value: self.acceptance_process,
            PaymentPlanActionType.REJECT.value:  self.acceptance_process
        }
        return actions_map

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
            PaymentPlanActionType.APPROVE.value: Approval.APPROVAL,
            PaymentPlanActionType.AUTHORIZE.value: Approval.AUTHORIZATION,
            PaymentPlanActionType.REVIEW.value: Approval.FINANCE_REVIEW,
            PaymentPlanActionType.REJECT.value: Approval.REJECT,
        }
        return actions_to_approval_type_map.get(self.action)

    def execute(self) -> PaymentPlan:
        """Get function from get_action_function and execute it
        return PaymentPlan object
        """
        self.validate_action()

        function_action = self.get_action_function()
        payment_plan = function_action()

        return payment_plan

    def validate_action(self):
        actions = self.get_actions_map().keys()
        if self.action not in actions:
            raise GraphQLError(
                f"Not Implemented Action: {self.action}. List of possible actions: {actions}"
            )

    def get_action_function(self):
        return self.get_actions_map().get(self.action)

    def send_for_approval(self):
        self.payment_plan.status_send_to_approval()
        self.payment_plan.save()
        # create new ApprovalProcess
        ApprovalProcess.objects.create(
            payment_plan=self.payment_plan,
            sent_for_approval_by=self.user,
            sent_for_approval_date=timezone.now()
        )
        return self.payment_plan

    def lock(self):
        # TODO: add more logic for lock action
        self.payment_plan.status_lock()
        self.payment_plan.save()

        return self.payment_plan

    def unlock(self):
        # TODO: add more logic for unlock action
        self.payment_plan.status_unlock()
        self.payment_plan.save()

        return self.payment_plan

    def acceptance_process(self):
        self.validate_payment_plan_status_to_acceptance_process_approval_type()

        # every time we will create Approval for last created AcceptanceProcess
        # init creation AcceptanceProcess added in send_for_approval()
        acceptance_process = self.payment_plan.acceptance_process.last()
        if not acceptance_process:
            logging.exception(f"Acceptance Process object not found for PaymentPlan {self.payment_plan.pk}")
            raise GraphQLError(f"Acceptance Process object not found for PaymentPlan {self.payment_plan.pk}")

        # validate approval required number
        self.validate_acceptance_process_approval_count(acceptance_process)

        approval_data = {
            "approval_process": acceptance_process,
            "created_by": self.user,
            "type": self.get_approval_type_by_action(),
            "comment": self.input_data.get("comment"),
        }
        Approval.objects.create(**approval_data)

        # base on approval required number check if we need update PaymentPlan status after creation new Approval
        self.check_payment_plan_and_update_status(acceptance_process)

        return self.payment_plan

    def validate_payment_plan_status_to_acceptance_process_approval_type(self):
        action_to_statuses_map = {
            PaymentPlanActionType.APPROVE.value: [PaymentPlan.Status.IN_APPROVAL],
            PaymentPlanActionType.AUTHORIZE.value: [PaymentPlan.Status.IN_AUTHORIZATION],
            PaymentPlanActionType.REVIEW.value: [PaymentPlan.Status.IN_REVIEW],
            PaymentPlanActionType.REJECT.value: [
                PaymentPlan.Status.IN_APPROVAL,
                PaymentPlan.Status.IN_AUTHORIZATION,
                PaymentPlan.Status.IN_REVIEW
            ]
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

    def check_payment_plan_and_update_status(self, acceptance_process):
        approval_type = self.get_approval_type_by_action()
        required_number = self.get_business_area_required_number_by_approval_type()

        if acceptance_process.approvals.filter(type=approval_type).count() >= required_number:
            if approval_type == Approval.APPROVAL:
                self.payment_plan.status_mark_as_approved()
                acceptance_process.sent_for_authorization_by = self.user
                acceptance_process.sent_for_authorization_date = timezone.now()
                acceptance_process.save()

            if approval_type == Approval.AUTHORIZATION:
                self.payment_plan.status_mark_as_authorized()
                acceptance_process.sent_for_finance_review_by = self.user
                acceptance_process.sent_for_finance_review_date = timezone.now()
                acceptance_process.save()

            if approval_type == Approval.FINANCE_REVIEW:
                self.payment_plan.status_mark_as_reviewed()

            if approval_type == Approval.REJECT:
                self.payment_plan.status_reject()

            self.payment_plan.save()
