import logging

from django.utils import timezone
from graphql import GraphQLError

from hct_mis_api.apps.payment.models import PaymentPlan, Approval


class PaymentPlanServices:
    @classmethod
    def validate_payment_plan_status(cls, status):
        if status not in (Approval.APPROVAL, Approval.AUTHORIZATION, Approval.FINANCE_REVIEW):
            msg = f"PaymentPlan status must be one of {Approval.APPROVAL}, {Approval.AUTHORIZATION} or {Approval.FINANCE_REVIEW}"
            raise GraphQLError(msg)

    @classmethod
    def payment_plan_update_status(cls, payment_plan, acceptance_process, status, user):
        business_area = payment_plan.business_area

        approval_count_map = {
            Approval.APPROVAL: business_area.approval_number,
            Approval.AUTHORIZATION: business_area.authorization_number,
            Approval.FINANCE_REVIEW: business_area.finance_review_number,
        }

        if acceptance_process.approvals.filter(type=status).count() >= approval_count_map.get(status):
            if status == Approval.APPROVAL:
                payment_plan.status_mark_as_approved()
                acceptance_process.authorized_by = user
                acceptance_process.authorization_date = timezone.now()
                acceptance_process.save()

            if status == Approval.AUTHORIZATION:
                payment_plan.status_mark_as_authorized()
                acceptance_process.finance_review_by = user
                acceptance_process.finance_review_date = timezone.now()
                acceptance_process.save()

            if status == Approval.FINANCE_REVIEW:
                payment_plan.status_mark_as_reviewed()

            payment_plan.save()
        return payment_plan

    @classmethod
    def create_reject_approval(cls, payment_plan, input_data, user):
        approval_process_obj = payment_plan.approval_process.last()
        if not approval_process_obj:
            logging.exception(f"ApprovalProcess object not found for PaymentPlan {payment_plan.pk}")
            raise GraphQLError("ApprovalProcess object not found")

        data = {
            "approval_process": approval_process_obj,
            "created_by": user,
            "type": Approval.REJECT,
            "comment": input_data.get("comment"),
        }
        Approval.objects.create(**data)

    @classmethod
    def create_approval(cls, payment_plan, input_data, user) -> PaymentPlan:
        status = input_data.get("status")
        cls.validate_payment_plan_status(status)
        acceptance_process = payment_plan.acceptance_process.last()

        data = {
            "approval_process": acceptance_process,
            "created_by": user,
            "type": status,
            "comment": input_data.get("comment"),
        }
        Approval.objects.create(**data)

        payment_plan = cls.payment_plan_update_status(payment_plan, acceptance_process, status, user)

        return payment_plan
