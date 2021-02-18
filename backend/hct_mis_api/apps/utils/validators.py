from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


DoubleSpaceValidator = RegexValidator(
    r"\s{2,}",
    _("Double spaces characters are not allowed."),
    inverse_match=True,
    code="double_spaces_characters_not_allowed",
)
StartEndSpaceValidator = RegexValidator(
    r"(^\s+)|(\s+$)",
    _("Leading or trailing spaces characters are not allowed."),
    inverse_match=True,
    code="leading_trailing_spaces_characters_not_allowed",
)
