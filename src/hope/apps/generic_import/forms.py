from constance import config
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.forms.widgets import Select
from django.utils import timezone

from hope.models import BusinessArea, Program, RoleAssignment


class BusinessAreaSelectWidget(Select):
    """Custom select widget that adds slug as data attribute."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):  # noqa: PLR0913
        """Override to add data-slug attribute to options."""
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            # Extract actual value from ModelChoiceIteratorValue if needed
            actual_value = value.value if hasattr(value, "value") else value
            if actual_value:
                # Get the BusinessArea object to extract slug
                try:
                    ba = BusinessArea.objects.get(pk=actual_value)
                    option["attrs"]["data-slug"] = ba.slug
                except (BusinessArea.DoesNotExist, ValueError, TypeError):
                    pass
        return option


class ProgramSelectWidget(Select):
    """Custom select widget that adds slug as data attribute."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):  # noqa: PLR0913
        """Override to add data-slug attribute to options."""
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            # Extract actual value from ModelChoiceIteratorValue if needed
            actual_value = value.value if hasattr(value, "value") else value
            if actual_value:
                # Get the Program object to extract slug
                try:
                    program = Program.objects.get(pk=actual_value)
                    option["attrs"]["data-slug"] = program.slug
                except (Program.DoesNotExist, ValueError, TypeError):
                    pass
        return option


class GenericImportForm(forms.Form):
    """Form for uploading generic import files with BA and Program selection."""

    business_area = forms.ModelChoiceField(
        queryset=BusinessArea.objects.none(),
        required=True,
        label="Business Area",
        empty_label="Select Business Area",
        widget=BusinessAreaSelectWidget(),
    )
    program = forms.CharField(
        required=True,
        label="Program",
        widget=forms.Select(choices=[("", "Select Program")]),
    )
    file = forms.FileField(
        required=True,
        label="Upload File",
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx,.xls"}),
    )

    def __init__(self, user, *args, **kwargs):
        """Initialize form with user-specific querysets.

        Args:
            user: Django user instance to filter accessible BAs and Programs
            *args: Variable positional arguments passed to parent
            **kwargs: Variable keyword arguments passed to parent

        """
        super().__init__(*args, **kwargs)
        self.user = user

        # Get accessible business areas for user
        business_areas = self._get_business_area_queryset()

        # Set business area queryset
        self.fields["business_area"].queryset = business_areas

        # If user has access to only one BA, pre-select it
        if business_areas.count() == 1:
            ba = business_areas.first()
            self.fields["business_area"].initial = ba

            # Get programs for the single BA
            programs = self._get_program_queryset(ba)

            # Set program field with ModelChoiceField and custom widget
            if programs.exists():
                self.fields["program"] = forms.ModelChoiceField(
                    queryset=programs,
                    widget=ProgramSelectWidget(),
                    required=True,
                    label="Program",
                    empty_label="Select Program",
                )

                # If only one program, pre-select it
                if programs.count() == 1:
                    self.fields["program"].initial = programs.first()
        # Programs will be filtered dynamically based on BA selection via JavaScript

    def _get_business_area_queryset(self) -> QuerySet[BusinessArea]:
        """Get business areas accessible to the user.

        Matches User.business_areas logic: includes partner assignments,
        excludes expired role assignments and inactive business areas.
        """
        # Superusers have access to all business areas
        if self.user.is_superuser:
            return BusinessArea.objects.exclude(active=False).distinct()

        # Match User.business_areas logic: include partner assignments, exclude expired/inactive
        partner_filter = Q(partner__user=self.user) if self.user.partner_id else Q(pk=None)

        role_assignments = RoleAssignment.objects.filter(Q(user=self.user) | partner_filter).exclude(
            expiry_date__lt=timezone.now()
        )

        # Get distinct business area IDs from role assignments
        ba_ids = role_assignments.values_list("business_area_id", flat=True).distinct()

        return BusinessArea.objects.filter(id__in=ba_ids).exclude(active=False).distinct()

    def _get_program_queryset(self, business_area: BusinessArea = None) -> QuerySet[Program]:
        """Get programs accessible to the user.

        Args:
            business_area: Optional BA to filter programs. If None, returns all accessible programs.

        """
        if business_area:
            program_ids = self.user.get_program_ids_for_business_area(business_area.id)
            return Program.objects.filter(
                id__in=program_ids,
                business_area=business_area,
                status=Program.ACTIVE,
            )
        # Return empty queryset if no BA is selected
        return Program.objects.none()

    def clean_program(self):
        """Validate program field and convert to Program object.

        Handles both CharField (dynamically loaded) and ModelChoiceField (pre-loaded) cases.
        """
        program = self.cleaned_data.get("program")

        if not program:
            raise ValidationError("Program is required.")

        # If already a Program object (from ModelChoiceField), return it
        if isinstance(program, Program):
            return program

        # Otherwise it's a string ID (from CharField), convert to Program
        try:
            program = Program.objects.get(pk=program)
        except (Program.DoesNotExist, ValueError):
            raise ValidationError("Selected program does not exist.")

        return program

    def clean_file(self):
        """Validate uploaded file."""
        file = self.cleaned_data.get("file")

        if not file:
            raise ValidationError("File is required.")

        # Check file extension
        if not file.name.endswith((".xlsx", ".xls")):
            raise ValidationError("Only Excel files (.xlsx, .xls) are allowed.")

        # Check file size
        max_size_mb = config.GENERIC_IMPORT_MAX_FILE_SIZE_MB
        max_size = max_size_mb * 1024 * 1024
        if file.size > max_size:
            raise ValidationError(
                f"File size must not exceed {max_size_mb} MB. Current size: {file.size / (1024 * 1024):.2f} MB"
            )

        return file

    def clean(self):
        """Validate that program belongs to selected business area."""
        cleaned_data = super().clean()
        business_area = cleaned_data.get("business_area")
        program = cleaned_data.get("program")

        if business_area and program:
            if program.business_area != business_area:
                raise ValidationError("Selected program does not belong to the selected business area.")

            # Verify user has access to this program
            program_ids = self.user.get_program_ids_for_business_area(business_area.id)
            if str(program.id) not in program_ids:
                raise ValidationError("You do not have access to the selected program.")

        return cleaned_data
