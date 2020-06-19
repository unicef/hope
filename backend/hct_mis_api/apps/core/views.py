from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django import forms
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import redirect, render
from graphene_django.settings import graphene_settings

from graphql.utils import schema_printer
from django.contrib.auth import logout


def homepage(request):
    return HttpResponse("", status=200)


def schema(request):
    schema = graphene_settings.SCHEMA
    my_schema_str = schema_printer.print_schema(schema)
    return HttpResponse(
        my_schema_str, content_type="application/graphlq", status=200
    )


def logout_view(request):
    logout(request)
    return redirect("/login")


class CommandForm(forms.Form):
    command = forms.CharField(label="Command", max_length=255, required=True)
    no_input = forms.BooleanField(label="No input", required=False)


@user_passes_test(lambda u: u.is_superuser)
def call_command_view(request):
    form = CommandForm()
    if request.method == "POST":
        form = CommandForm(request.POST)
        if form.is_valid():
            if form.data.get("no_input", False):
                call_command(form.data["command"], "--noinput")
            else:
                call_command(form.data["command"])

    return render(request, "core/call_command.html", {"form": form})


def trigger_error(request):
    division_by_zero = 1 / 0
