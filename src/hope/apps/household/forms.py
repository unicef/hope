from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.db import Error
from django.db.models import QuerySet
from django.forms import HiddenInput
from django.utils.translation import gettext_lazy as _

from hope.admin.steficon import AutocompleteWidget
from hope.apps.core.models import BusinessArea
from hope.apps.household.models import (
    Household,
    Individual,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    XlsxUpdateFile,
)
from hope.apps.program.models import Program, ProgramCycle
from hope.apps.registration_data.models import RegistrationDataImport


def get_households_from_text(program: Program, text: Any, target_field: Any, separator: Any) -> QuerySet | list:
    """Given a text and a BA, find all the Households ID in the text and return the valid IDs in that business area."""
    if separator in ["space", "tab"]:
        list_of_households = list(map(str.strip, text.split(" ")))
    elif separator == "new_line":
        list_of_households = list(map(str.strip, text.splitlines()))
    else:
        list_of_households = list(map(str.strip, text.split(separator)))
    if target_field == "unicef_id":
        return Household.objects.filter(unicef_id__in=list_of_households, program=program)
    if target_field == "unique_id":
        return Household.objects.filter(
            id__in=list_of_households,
            program=program,
        )
    return []


class UpdateByXlsxStage1Form(forms.Form):
    business_area = forms.ModelChoiceField(
        queryset=BusinessArea.objects.all().order_by("name"),
        required=True,
        widget=AutocompleteWidget(BusinessArea, ""),
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.filter(status=Program.ACTIVE).order_by("name"),
        required=True,
        widget=AutocompleteWidget(Program, ""),
    )
    registration_data_import = forms.ModelChoiceField(
        queryset=RegistrationDataImport.objects.all().order_by("name"),
        required=True,
        widget=AutocompleteWidget(RegistrationDataImport, ""),
    )
    file = forms.FileField(required=True, help_text="Select XLSX file")

    def clean_program(self) -> Program | None:
        program = self.cleaned_data.get("program")
        ba = self.cleaned_data.get("business_area")
        if program.business_area != ba:
            self.add_error("program", "Program should belong to selected business area.")
        return program

    def clean_registration_data_import(self) -> RegistrationDataImport | None:
        data: RegistrationDataImport | None = self.cleaned_data.get("registration_data_import")
        program: Program = self.cleaned_data["program"]

        if not data:
            return None

        registration_data_import = self._retrieve_rdi_by_name()

        self._check_rdi_has_correct_business_area(registration_data_import, program)

        return registration_data_import

    def _check_rdi_has_correct_business_area(
        self, registration_data_import: RegistrationDataImport, program: Program
    ) -> None:
        business_area = self.cleaned_data.get("business_area")
        if registration_data_import.business_area != business_area:
            raise ValidationError("Rdi should belong to selected business area")
        if getattr(registration_data_import, "program", None) != program:
            raise ValidationError("Rdi should belong to selected Program")

    def _retrieve_rdi_by_name(self) -> RegistrationDataImport:
        data = self.cleaned_data.get("registration_data_import")
        registration_data_import = RegistrationDataImport.objects.filter(name=data).first()
        if not registration_data_import:
            raise ValidationError(f"Rdi with the name {data} doesn't exist")
        return registration_data_import


class UpdateByXlsxStage2Form(forms.Form):
    xlsx_update_file = forms.ModelChoiceField(queryset=XlsxUpdateFile.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.xlsx_columns = kwargs.pop("xlsx_columns", [])
        super().__init__(*args, **kwargs)
        self.fields["xlsx_match_columns"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[(xlsx_column, xlsx_column) for xlsx_column in self.xlsx_columns],
        )

    def clean_xlsx_match_columns(self) -> dict:
        data = self.cleaned_data["xlsx_match_columns"]
        required_columns = {"individual__unicef_id", "household__unicef_id"}
        all_columns = set(self.xlsx_columns)
        required_columns_in_this_form = all_columns & required_columns
        columns_not_found = required_columns_in_this_form - set(data)
        if not len(columns_not_found):
            return data
        raise ValidationError("Unicef Id columns have to be selected")


class UpdateIndividualsIBANFromXlsxForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    file = forms.FileField()


class WithdrawForm(forms.Form):
    reason = forms.CharField(label="Log message", max_length=100, required=False)
    tag = forms.SlugField(
        max_length=100,
        required=False,
        help_text="HH will have a user_field with this name with value 'True'",
    )


class RestoreForm(forms.Form):
    reason = forms.CharField(label="Log message", max_length=100, required=False)
    reopen_tickets = forms.BooleanField(required=False, help_text="Restore all previously closed tickets")


class MassWithdrawForm(WithdrawForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


class MassRestoreForm(RestoreForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


class CreateTargetPopulationTextForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField()
    target_field = forms.ChoiceField(choices=(("unicef_id", _("Unicef ID")), ("unique_id", _("UUID"))))
    separator = forms.ChoiceField(
        choices=(
            (",", _("Comma")),
            ("new_line", _("New line")),
            ("space", _("Space")),
            (";", _("Semi colon")),
            ("tab", _("Tab")),
        )
    )
    criteria = forms.CharField(
        widget=forms.Textarea,
        help_text=_("List of either UUID4 or UNICEF IDs separated the separator"),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.program = kwargs.pop("program")
        if not self.program:
            raise forms.ValidationError("Missing programme")
        read_only = kwargs.pop("read_only", False)
        super().__init__(*args, **kwargs)
        self.fields["program_cycle"] = forms.ModelChoiceField(
            queryset=ProgramCycle.objects.filter(program=self.program),
            label="Programme Cycle",
        )

        if read_only:
            self.fields["name"].widget = HiddenInput()
            self.fields["criteria"].widget = HiddenInput()
            self.fields["target_field"].widget = HiddenInput()
            self.fields["separator"].widget = HiddenInput()
            self.fields["program_cycle"].widget = HiddenInput()

    def clean_criteria(self) -> list | None:
        try:
            return get_households_from_text(  # type: ignore
                self.program,
                self.cleaned_data["criteria"],
                self.cleaned_data["target_field"],
                self.cleaned_data["separator"],
            )
        except (KeyError, Error) as e:
            raise ValidationError(str(e))


class MassEnrollForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput, required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.business_area_id = kwargs.pop("business_area_id")
        self.households = kwargs.pop("households")
        super().__init__(*args, **kwargs)
        self.fields["program_for_enroll"] = forms.ModelChoiceField(
            queryset=Program.objects.filter(business_area_id=self.business_area_id, status=Program.ACTIVE),
            label="Select a program to enroll households to",
        )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if "apply" in self.data:
            program_for_enroll = cleaned_data.get("program_for_enroll")
            warning_message = None  # Initialize the warning message
            # Check each household in the queryset
            for household in self.households:
                if not (
                    household.program
                    and household.program.data_collecting_type
                    and program_for_enroll.data_collecting_type
                    and program_for_enroll.data_collecting_type
                    in household.program.data_collecting_type.compatible_types.all()
                ):
                    # Set the warning message
                    warning_message = (
                        "Not all households have data collecting type compatible with the selected program"
                    )
                    break  # Exit the loop after the first incompatible household

            if self.households.exclude(program__beneficiary_group=program_for_enroll.beneficiary_group).exists():
                self.add_error(
                    None,
                    "Some households belong to a different beneficiary group than the selected program.",
                )

            if warning_message:
                # Add the warning message as a non-field error
                self.add_error(None, warning_message)

        return cleaned_data


# used in UkraineBaseRegistrationService
class IndividualForm(forms.ModelForm):
    class Meta:
        model = Individual
        fields = []  # dynamically set in __init__

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        data = kwargs.get("data")
        self.Meta.fields = list(data.keys()) if data else "__all__"  # type: ignore

        super().__init__(*args, **kwargs)

        # override queryset for Individual
        if "individual" in self.Meta.fields:
            data["individual"] = data["individual"].pk  # type: ignore
            self.fields["individual"].queryset = PendingIndividual.objects.all()

        if "household" in self.Meta.fields:
            self.fields["household"].queryset = PendingHousehold.objects.all()


# used in UkraineBaseRegistrationService
class DocumentForm(forms.ModelForm):
    class Meta:
        model = PendingDocument
        fields = []  # dynamically set in __init__

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        data = kwargs.get("data")
        self.Meta.fields = list(data.keys()) if data else "__all__"  # type: ignore
        super().__init__(*args, **kwargs)

        # override queryset for Individual
        if "individual" in self.Meta.fields:
            self.fields["individual"].queryset = PendingIndividual.objects.all()


class WithdrawHouseholdsForm(forms.Form):
    business_area = forms.ModelChoiceField(
        queryset=BusinessArea.objects.all().order_by("name"),
        required=True,
        widget=AutocompleteWidget(BusinessArea, ""),
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.none(),
        required=True,
        widget=None,
    )
    household_list = forms.CharField(widget=forms.Textarea, required=True, label="Household IDs")
    tag = forms.CharField(required=True, label="Tag")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        business_area = kwargs.pop("business_area", None)
        super().__init__(*args, **kwargs)
        if business_area:
            self.fields["program"].queryset = Program.objects.filter(
                business_area=business_area, status=Program.ACTIVE
            ).order_by("name")
            self.fields["program"].widget = AutocompleteWidget(Program, "", business_area=business_area)
