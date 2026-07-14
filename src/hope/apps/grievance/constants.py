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


# Callable choices wrappers: passed to model fields as ``choices=get_*_choices`` so that
# changing the underlying tuple does not generate a (no-op) migration.
def get_priority_choices() -> tuple:
    return PRIORITY_CHOICES


def get_urgency_choices() -> tuple:
    return URGENCY_CHOICES
