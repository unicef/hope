from django.forms import Form, CharField, ChoiceField, Textarea
from django.forms.models import BaseInlineFormSet, ModelForm
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from account.models import Role, IncompatibleRoles, UserRole
from core.models import BusinessArea


class LoadUsersForm(Form):
    emails = CharField(widget=Textarea)
    business_area = ChoiceField(choices=[(ba.id, ba.name) for ba in BusinessArea.objects.all()])
    role = ChoiceField(choices=[(role.id, role.name) for role in Role.objects.all()])


class UserRoleAdminForm(ModelForm):
    def clean(self):
        super().clean()
        role = self.cleaned_data["role"]
        incompatible_roles = list(
            IncompatibleRoles.objects.filter(role_one=role).values_list("role_two", flat=True)
        ) + list(IncompatibleRoles.objects.filter(role_two=role).values_list("role_one", flat=True))
        incompatible_userroles = UserRole.objects.filter(
            business_area=self.cleaned_data["business_area"],
            role__id__in=incompatible_roles,
            user=self.cleaned_data["user"],
        )
        if self.instance.id:
            incompatible_userroles = incompatible_userroles.exclude(id=self.instance.id)
        if incompatible_userroles.exists():
            raise ValidationError(
                {
                    "role": _(
                        f"This role is incompatible with {', '.join([userrole.role.name for userrole in incompatible_userroles])}"
                    )
                }
            )


class UserRoleInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                business_area = form.cleaned_data["business_area"]
                role = form.cleaned_data["role"]
                incompatible_roles = list(
                    IncompatibleRoles.objects.filter(role_one=role).values_list("role_two", flat=True)
                ) + list(IncompatibleRoles.objects.filter(role_two=role).values_list("role_one", flat=True))
                error_forms = [
                    form_two.cleaned_data["role"].name
                    for form_two in self.forms
                    if not form_two.cleaned_data.get("DELETE")
                    and form_two.cleaned_data["business_area"] == business_area
                    and form_two.cleaned_data["role"].id in incompatible_roles
                ]
                if error_forms:
                    if "role" not in form._errors:
                        form._errors["role"] = ErrorList()
                    form._errors["role"].append(_(f"{role.name} is incompatible with {', '.join(error_forms)}."))
