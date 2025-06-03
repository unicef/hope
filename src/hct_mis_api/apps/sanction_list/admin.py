import logging

from django.conf import settings
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.http.request import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from django.shortcuts import render

from hct_mis_api.apps.sanction_list.models import (
    SanctionList,
    SanctionListIndividual,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from admin_extra_buttons.decorators import button
from django.contrib import messages
from django import forms

import os
from django.shortcuts import render
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def handle_uploaded_file(obj_detail: str, f: UploadedFile):
    upload_folder = os.path.join(settings.MEDIA_ROOT, 'sanction_lists', obj_detail)
    os.makedirs(upload_folder, exist_ok=True)
    upload_path = os.path.join(upload_folder, f.name)
    with default_storage.open(upload_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return upload_path


def get_newest_file_in_folder(folder: str) -> str | None:
    folder_path = os.path.join(settings.MEDIA_ROOT, folder)

    if not os.path.isdir(folder_path):
        return None  # Folder doesn't exist

    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    if not files:
        return None

    newest_file = min(files, key=os.path.getmtime)
    relative_path = os.path.relpath(newest_file, settings.MEDIA_ROOT)
    return relative_path  # Return relative path for use with MEDIA_URL


class UploadFileForm(forms.Form):
    file = forms.FileField()


class SearchForm(forms.Form):
    text = forms.TextInput()




@admin.register(SanctionList)
class SanctionListAdmin(HOPEModelAdminBase):
    list_display = ("name", )
    search_fields = ("name", )

    @button(label="Upload new version", permission="account.can_sync_with_ad")
    def upload(self, request: HttpRequest, pk: int) -> HttpResponse:
        ctx = self.get_common_context(request)
        obj = SanctionList.objects.get(pk=pk)
        ctx["obj"] = obj
        if request.method == "POST":
            form = UploadFileForm(request.POST, request.FILES)
            try:
                if "upload" in request.POST and form.is_valid():
                    handle_uploaded_file(str(obj.pk), request.FILES['file'])
                    self.message_user(request, "New version has been uploaded!", messages.SUCCESS)
            except BaseException as e:
                messages.add_message(request, messages.ERROR, str(e))
        else:
            form = UploadFileForm()

        ctx["form"] = form
        return render(request, "sanction_list/upload.html", ctx)


    @button(label="Process", permission="account.can_sync_with_ad")
    def process(self, request: HttpRequest, pk: int) -> None:
        """Put latest version of the file in Redis"""
        ctx = self.get_common_context(request)
        obj = SanctionList.objects.get(pk=pk)
        ctx["obj"] = obj

        folder_path = os.path.join(settings.MEDIA_ROOT, 'sanction_lists', str(obj.pk))
        newest_file = get_newest_file_in_folder(folder_path)
        print(111, newest_file)
        self.message_user(request, "Put newest version of the file in Redis", messages.SUCCESS)

    @button(label="Check", permission="account.can_sync_with_ad")
    def checking(self, request: HttpRequest, pk: int) -> None:
        """check file against input values"""
        self.message_user(request, "Check file against input values", messages.SUCCESS)

    @button(label="Show", permission="account.can_sync_with_ad")
    def show(self, request: HttpRequest, pk: int) -> None:
        """Show values based on the latest version"""
        self.message_user(request, "how values based on the latest version", messages.SUCCESS)


class SanctionListIndividualDateOfBirthAdmin(admin.StackedInline):
    model = SanctionListIndividualDateOfBirth
    extra = 0


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "listed_on", "un_list_type", "reference_number", "country_of_birth", "active")
    search_fields = (
        "full_name",
        "first_name",
        "second_name",
        "third_name",
        "fourth_name",
        "name_original_script",
        "reference_number",
    )
    list_filter = ("un_list_type", "active", ("country_of_birth", AutoCompleteFilter))
    inlines = (SanctionListIndividualDateOfBirthAdmin,)
    raw_id_fields = ("country_of_birth",)


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type_of_document", "date_of_issue", "issuing_country")
    raw_id_fields = ("individual", "issuing_country")
    list_filter = (("issuing_country", AutoCompleteFilter), "type_of_document")
    search_fields = ("document_number",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "issuing_country")
