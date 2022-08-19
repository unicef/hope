from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.conf import settings

from .models import GrievanceTicket, TicketComplaintDetails, TicketSensitiveDetails
from ..household.models import Household


URGENCY_CHOICES = {
    1: "Very urgent",
    2: "Urgent",
    3: "Not urgent",
}

PRIORITY_CHOICES = {
    1: "High",
    2: "Medium",
    3: "Low",
}

CATEGORY_CHOICES = {
    1: "Payment Verification",
    2: "Data Change",
    3: "Sensitive Grievance",
    4: "Grievance Complaint",
    5: "Negative Feedback",
    6: "Referral",
    7: "Positive Feedback",
    8: "Needs Adjudication",
    9: "System Flagging",
}

STATUS_CHOICES = {
    1: "New",
    2: "Assigned",
    3: "In Progress",
    4: "On Hold",
    5: "For Approval",
    6: "Closed",
}

ISSUE_TYPES_CHOICES = {
    2: {
        13: "Household Data Update",
        14: "Individual Data Update",
        15: "Withdraw Individual",
        16: "Add Individual",
        17: "Withdraw Household",
    },
    3: {
        1: "Data breach",
        2: "Bribery, corruption or kickback",
        3: "Fraud and forgery",
        4: "Fraud involving misuse of programme funds by third party",
        5: "Harassment and abuse of authority",
        6: "Inappropriate staff conduct",
        7: "Unauthorized use, misuse or waste of UNICEF property or funds",
        8: "Conflict of interest",
        9: "Gross mismanagement",
        10: "Personal disputes",
        11: "Sexual harassment and sexual exploitation",
        12: "Miscellaneous",
    },
}


@registry.register_document
class GrievanceTicketDocument(Document):
    unicef_id = fields.KeywordField(similarity="boolean")
    created_at = fields.DateField()
    assigned_to = fields.KeywordField(similarity="boolean")
    registration_data_import = fields.TextField()
    household_unicef_id = fields.KeywordField(similarity="boolean")
    status = fields.KeywordField(similarity="boolean")
    issue_type = fields.TextField()
    category = fields.KeywordField(similarity="boolean")
    admin = fields.KeywordField(similarity="boolean")
    priority = fields.KeywordField(similarity="boolean")
    urgency = fields.KeywordField(similarity="boolean")
    grievance_type = fields.KeywordField(similarity="boolean")
    head_of_household_last_name = fields.KeywordField(similarity="boolean")
    business_area = fields.KeywordField(similarity="boolean")
    fsp = fields.KeywordField(similarity="boolean")

    def prepare_assigned_to(self, instance):
        if instance.assigned_to:
            return instance.assigned_to.id

    def prepare_registration_data_import(self, instance):
        if instance.registration_data_import:
            return instance.registration_data_import.id

    def prepare_status(self, instance):
        return STATUS_CHOICES.get(instance.status)

    def prepare_issue_type(self, instance):
        if instance.category in range(2, 4):
            return ISSUE_TYPES_CHOICES[instance.category].get(instance.issue_type)

    def prepare_category(self, instance):
        return CATEGORY_CHOICES.get(instance.category)

    def prepare_admin2_new(self, instance):
        if instance.admin2_new:
            return instance.admin2_new.id

    def prepare_priority(self, instance):
        return PRIORITY_CHOICES.get(instance.priority)

    def prepare_urgency(self, instance):
        return URGENCY_CHOICES.get(instance.urgency)

    def prepare_grievance_type(self, instance):
        return "user" if instance.category in range(2, 8) else "system"

    def prepare_head_of_household_last_name(self, instance):
        household_unicef_id = instance.household_unicef_id
        if household_unicef_id:
            household = Household.objects.filter(unicef_id=household_unicef_id).first()
            return household.head_of_household.family_name

    def prepare_business_area(self, instance):
        return instance.business_area.slug

    def prepare_fsp(self, instance):
        if instance.ticket_details:
            if isinstance(instance.ticket_details, (TicketComplaintDetails, TicketSensitiveDetails)):
                if instance.ticket_details.payment_record:
                    return instance.ticket_details.payment_record.service_provider.full_name

    class Django:
        model = GrievanceTicket

    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}grievance_tickets"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
