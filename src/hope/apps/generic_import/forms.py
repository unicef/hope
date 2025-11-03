from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from hope.apps.core.models import BusinessArea
from hope.apps.program.models import Program


class GenericImportForm(forms.Form):
    """Form for uploading generic import files with BA and Program selection."""

    business_area = forms.ModelChoiceField(
        queryset=BusinessArea.objects.none(),
        required=True,
        label="Business Area",
        empty_label="Select Business Area",
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.none(),
        required=True,
        label="Program",
        empty_label="Select Program",
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

        """
        super().__init__(*args, **kwargs)
        self.user = user

        # Get accessible business areas for user
        business_areas = self._get_business_area_queryset()

        # If user has access to only one BA, hide the field and set default
        if business_areas.count() == 1:
            self.fields["business_area"].widget = forms.HiddenInput()
            self.fields["business_area"].initial = business_areas.first()
            self.fields["business_area"].queryset = business_areas

            # Get programs for the single BA
            programs = self._get_program_queryset(business_areas.first())

            # If user has access to only one program, hide that field too
            if programs.count() == 1:
                self.fields["program"].widget = forms.HiddenInput()
                self.fields["program"].initial = programs.first()
                self.fields["program"].queryset = programs
            else:
                self.fields["program"].queryset = programs
        else:
            self.fields["business_area"].queryset = business_areas
            # Programs will be filtered dynamically based on BA selection

    def _get_business_area_queryset(self) -> QuerySet[BusinessArea]:
        """Get business areas accessible to the user."""
        return BusinessArea.objects.filter(role_assignments__user=self.user).distinct()

    def _get_program_queryset(self, business_area: BusinessArea = None) -> QuerySet[Program]:
        """Get programs accessible to the user.

        Args:
            business_area: Optional BA to filter programs. If None, returns all accessible programs.

        """
        from hope.apps.account.models import get_program_ids_for_business_area

        if business_area:
            program_ids = get_program_ids_for_business_area(self.user, business_area.id)
            return Program.objects.filter(
                id__in=program_ids,
                business_area=business_area,
                status=Program.ACTIVE,
            )
        # Return empty queryset if no BA is selected
        return Program.objects.none()

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
            from hope.apps.account.models import get_program_ids_for_business_area

            program_ids = get_program_ids_for_business_area(self.user, business_area.id)
            if program.id not in program_ids:
                raise ValidationError("You do not have access to the selected program.")

        return cleaned_data
