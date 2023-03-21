from django import forms

from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation


class TargetPopulationForm(forms.ModelForm):
    class Meta:
        model = TargetPopulation
        exclude = ["id"]

    def clean_program(self) -> Program:
        program = self.cleaned_data["program"]
        if program is None or program.status == "FINISHED":
            raise forms.ValidationError("Program must be set and active")
        elif program.business_area != self.cleaned_data["business_area"]:
            raise forms.ValidationError("The program must be opened in the business_area")
        return program
