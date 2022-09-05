from django import forms
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _


class ProductionLoginForm(forms.Form):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(username)s and password. Note that both " "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }
