from django.utils.translation import gettext_lazy as _

PRIORITY_HIGH = 1
PRIORITY_MEDIUM = 2
PRIORITY_LOW = 3
PRIORITY_CHOICES = (
    (PRIORITY_HIGH, _("High")),
    (PRIORITY_MEDIUM, _("Medium")),
    (PRIORITY_LOW, _("Low")),
)

URGENCY_VERY_URGENT = 1
URGENCY_URGENT = 2
URGENCY_NOT_URGENT = 3
URGENCY_CHOICES = (
    (URGENCY_VERY_URGENT, _("Very urgent")),
    (URGENCY_URGENT, _("Urgent")),
    (URGENCY_NOT_URGENT, _("Not urgent")),
)


ES_MAPPING_PRIORITY_CHOICES = {
        1: "High",
        2: "Medium",
        3: "Low",
    }

ES_MAPPING_URGENCY_CHOICES = {
    1: "Very urgent",
    2: "Urgent",
    3: "Not urgent",
}

ES_MAPPING_STATUS_CHOICES = {
    1: "New",
    2: "Assigned",
    3: "In Progress",
    4: "On Hold",
    5: "For Approval",
    6: "Closed",
}

ES_MAPPING_CATEGORY_CHOICES = {
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

ES_MAPPING_ISSUE_TYPES_CHOICES = {
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