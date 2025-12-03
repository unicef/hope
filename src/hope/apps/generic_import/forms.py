from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.forms.widgets import Select
from django.utils import timezone

from hope.apps.account.models import RoleAssignment
from hope.apps.core.models import BusinessArea
from hope.apps.program.models import Program


class BusinessAreaSelectWidget(Select):
    """Custom select widget that adds slug as data attribute."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
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

        # If user has access to only one BA, pre-select and disable it
        if business_areas.count() == 1:
            ba = business_areas.first()
            self.fields["business_area"].initial = ba
            self.fields["business_area"].widget.attrs["disabled"] = True

            # Get programs for the single BA
            programs = self._get_program_queryset(ba)

            # Set program choices
            if programs.exists():
                program_choices = [("", "Select Program")] + [(p.id, p.name) for p in programs]
                self.fields["program"].widget = forms.Select(choices=program_choices)

                # If only one program, pre-select and disable it
                if programs.count() == 1:
                    self.fields["program"].initial = programs.first().id
                    self.fields["program"].widget.attrs["disabled"] = True
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

        Since we're using CharField instead of ModelChoiceField to avoid
        queryset validation issues with dynamically loaded programs.
        """
        program_id = self.cleaned_data.get("program")

        if not program_id:
            raise ValidationError("Program is required.")

        try:
            program = Program.objects.get(pk=program_id)
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

        # Check file size (limit to 50MB)
        max_size = 50 * 1024 * 1024  # 50 MB
        if file.size > max_size:
            raise ValidationError(f"File size must not exceed 50 MB. Current size: {file.size / (1024 * 1024):.2f} MB")

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
