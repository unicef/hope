from django.core.validators import RegexValidator

from hope.apps.household.const import RDI_SOURCES

validate_originating_id = RegexValidator(
    regex=rf"^({'|'.join(RDI_SOURCES)})#.+$",
    message=f"originating_id must start with: {', '.join(RDI_SOURCES)}",
)
