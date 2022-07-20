import logging

from django.utils import timezone
from graphql import GraphQLError

from hct_mis_api.apps.payment.models import PaymentPlan, Approval, ApprovalProcess


class PaymentPlanServices:
    def __init__(self, payment_plan, action, info, input_data):
        self.payment_plan = payment_plan
        self.action = action
        self.info = info
        self.input_data = input_data
        self.user = self.info.context.user

    def get_action_function(self):
        action_map = {
            "LOCK": self.lock,
            "UNLOCK": self.unlock,
            "SEND_FOR_APPROVAL": self.send_for_approval,
            "REJECT": self.reject,
            "ACCEPTANCE_PROCESS": self.acceptance_process_create,
        }

        return action_map.get(self.action)

    def execute(self) -> PaymentPlan:
        """Get function from get_action_function and execute it
        return PaymentPlan object
        """

        function_action = self.get_action_function()
        payment_plan = function_action()

        return payment_plan

    def send_for_approval(self):
        self.payment_plan.status_send_to_approval()
        self.payment_plan.save()

        ApprovalProcess.objects.create(
            payment_plan=self.payment_plan, approved_by=self.user, approve_date=timezone.now()
        )

        return self.payment_plan

    def lock(self):
        # TODO: add more logic for lock action

        self.payment_plan.status_lock()
        self.payment_plan.save()

        return self.payment_plan

    def unlock(self):
        self.payment_plan.status_unlock()
        self.payment_plan.save()

        return self.payment_plan

    def reject(self):
        self.payment_plan.status_reject()
        self.payment_plan.save()

        approval_process_obj = self.payment_plan.approval_process.last()
        if not approval_process_obj:
            logging.exception(f"ApprovalProcess object not found for PaymentPlan {self.payment_plan.pk}")
            raise GraphQLError("ApprovalProcess object not found")

        data = {
            "approval_process": approval_process_obj,
            "created_by": self.user,
            "type": Approval.REJECT,
            "comment": self.input_data.get("comment"),
        }
        Approval.objects.create(**data)
        return self.payment_plan

    def acceptance_process_create(self):
        statuses_list = (
            PaymentPlan.Status.IN_APPROVAL,
            PaymentPlan.Status.IN_AUTHORIZATION,
            PaymentPlan.Status.IN_REVIEW,
        )
        if self.payment_plan.status not in statuses_list:
            raise GraphQLError(f"Add Acceptance Process is possible for PaymentPlan with status {statuses_list}")

        acceptance_process_type = self.input_data.get("acceptance_process_type")
        self.validate_payment_plan_status(acceptance_process_type)
        # every time we will create Approval for last created AcceptanceProcess
        # init creation AcceptanceProcess added in send_for_approval()
        acceptance_process = self.payment_plan.acceptance_process.last()
        if not acceptance_process:
            logging.exception(f"ApprovalProcess object not found for PaymentPlan {self.payment_plan.pk}")
            raise GraphQLError("ApprovalProcess object not found")

        data = {
            "approval_process": acceptance_process,
            "created_by": self.user,
            "type": acceptance_process_type,
            "comment": self.input_data.get("comment"),
        }
        Approval.objects.create(**data)

        # check if we need update PaymentPlan status
        self.check_payment_plan_update_status(acceptance_process)

        return self.payment_plan

    @staticmethod
    def validate_payment_plan_status(acceptance_process_type):
        acceptance_process_types_list = (Approval.APPROVAL, Approval.AUTHORIZATION, Approval.FINANCE_REVIEW)
        if acceptance_process_type not in acceptance_process_types_list:
            msg = f"PaymentPlan acceptance process type must be one of {acceptance_process_types_list}"
            raise GraphQLError(msg)

    def check_payment_plan_update_status(self, acceptance_process):
        business_area = self.payment_plan.business_area

        approval_count_map = {
            Approval.APPROVAL: business_area.approval_number_required,
            Approval.AUTHORIZATION: business_area.authorization_number_required,
            Approval.FINANCE_REVIEW: business_area.finance_review_number_required,
        }
        acceptance_process_type = self.input_data.get("acceptance_process_type")

        if acceptance_process.approvals.filter(type=acceptance_process_type).count() >= approval_count_map.get(
            acceptance_process_type
        ):
            if acceptance_process_type == Approval.APPROVAL:
                self.payment_plan.status_mark_as_approved()
                acceptance_process.authorized_by = self.user
                acceptance_process.authorization_date = timezone.now()
                acceptance_process.save()

            if acceptance_process_type == Approval.AUTHORIZATION:
                self.payment_plan.status_mark_as_authorized()
                acceptance_process.finance_review_by = self.user
                acceptance_process.finance_review_date = timezone.now()
                acceptance_process.save()

            if acceptance_process_type == Approval.FINANCE_REVIEW:
                self.payment_plan.status_mark_as_reviewed()

            self.payment_plan.save()
