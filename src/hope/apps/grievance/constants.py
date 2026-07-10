from django.utils.translation import gettext_lazy as _

PRIORITY_NOT_SET = 0
PRIORITY_HIGH = 1
PRIORITY_MEDIUM = 2
PRIORITY_LOW = 3
PRIORITY_CHOICES = (
    (PRIORITY_NOT_SET, _("Not set")),
    (PRIORITY_HIGH, _("High")),
    (PRIORITY_MEDIUM, _("Medium")),
    (PRIORITY_LOW, _("Low")),
)

URGENCY_NOT_SET = 0
URGENCY_VERY_URGENT = 1
URGENCY_URGENT = 2
URGENCY_NOT_URGENT = 3
URGENCY_CHOICES = (
    (URGENCY_NOT_SET, _("Not set")),
    (URGENCY_VERY_URGENT, _("Very urgent")),
    (URGENCY_URGENT, _("Urgent")),
    (URGENCY_NOT_URGENT, _("Not urgent")),
)

# Submission channel a grievance came in through. The MANUAL channels are user-selectable on
# creation; HOPE is reserved for system-generated tickets (set automatically, not selectable).
SUBMISSION_CHANNEL_CALL_CENTER = 1
SUBMISSION_CHANNEL_REDRESSAL_DESK = 2
SUBMISSION_CHANNEL_COMMUNITY_OUTREACH = 3
SUBMISSION_CHANNEL_SUGGESTION_BOX = 4
SUBMISSION_CHANNEL_HOPE = 5
SUBMISSION_CHANNEL_MANUAL_CHOICES = (
    (SUBMISSION_CHANNEL_CALL_CENTER, _("Call Center")),
    (SUBMISSION_CHANNEL_REDRESSAL_DESK, _("Grievances Redressal Desk at Distribution Site")),
    (SUBMISSION_CHANNEL_COMMUNITY_OUTREACH, _("Community Outreach")),
    (SUBMISSION_CHANNEL_SUGGESTION_BOX, _("Suggestion Boxes")),
)
SUBMISSION_CHANNEL_CHOICES = SUBMISSION_CHANNEL_MANUAL_CHOICES + ((SUBMISSION_CHANNEL_HOPE, _("HOPE Generated")),)


# Callable choices wrappers: passed to model fields as ``choices=get_*_choices`` so that
# changing the underlying tuple does not generate a (no-op) migration.
def get_priority_choices() -> tuple:
    return PRIORITY_CHOICES


def get_urgency_choices() -> tuple:
    return URGENCY_CHOICES


def get_submission_channel_choices() -> tuple:
    return SUBMISSION_CHANNEL_CHOICES


def get_submission_channel_manual_choices() -> tuple:
    return SUBMISSION_CHANNEL_MANUAL_CHOICES
