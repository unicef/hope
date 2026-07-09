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

# Submission channel a manually-created grievance came in through. System-generated tickets
# have no channel and stay null.
SOURCE_CALL_CENTER = 1
SOURCE_REDRESSAL_DESK = 2
SOURCE_COMMUNITY_OUTREACH = 3
SOURCE_SUGGESTION_BOX = 4
SOURCE_CHOICES = (
    (SOURCE_CALL_CENTER, _("Call Center")),
    (SOURCE_REDRESSAL_DESK, _("Grievances Redressal Desk at Distribution Site")),
    (SOURCE_COMMUNITY_OUTREACH, _("Community Outreach")),
    (SOURCE_SUGGESTION_BOX, _("Suggestion Boxes")),
)


# Callable choices wrappers: passed to model fields as ``choices=get_*_choices`` so that
# changing the underlying tuple does not generate a (no-op) migration.
def get_priority_choices() -> tuple:
    return PRIORITY_CHOICES


def get_urgency_choices() -> tuple:
    return URGENCY_CHOICES


def get_source_choices() -> tuple:
    return SOURCE_CHOICES
