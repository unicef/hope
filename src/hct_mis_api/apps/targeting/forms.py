from django import forms

from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program


class TargetPopulationForm(forms.ModelForm):
    class Meta:
        model = PaymentPlan
        exclude = ["id"]

    def clean_program(self) -> Program:
        program = self.cleaned_data["program"]
        if program is None or program.status == "FINISHED":
            raise forms.ValidationError("Program must be set and active")
        if program.business_area != self.cleaned_data.get("business_area"):
            raise forms.ValidationError("The program must be opened in the business_area")
        return program
