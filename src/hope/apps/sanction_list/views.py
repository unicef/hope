from tempfile import NamedTemporaryFile

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views.generic.edit import CreateView

from hope.apps.sanction_list.models import SanctionList, UploadedXLSXFile
from hope.apps.sanction_list.template_generator import get_template_file


class UploadForm(forms.ModelForm):
    file = forms.FileField(required=True, widget=forms.ClearableFileInput)
    selected_lists = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, queryset=SanctionList.objects.all()
    )

    class Meta:
        model = UploadedXLSXFile
        fields = ["selected_lists", "file"]


class UploadFileView(LoginRequiredMixin, CreateView):
    template_name = "sanction_list/upload.html"
    model = UploadedXLSXFile
    form_class = UploadForm
    success_url = "."

    def form_valid(self, form: UploadForm) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.associated_email = self.request.user.email
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, "File Uploaded")
        return super().form_valid(form)


@login_required
def download_sanction_template(request: HttpRequest) -> HttpResponse:
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "sanction_list_check_template.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"

    wb = get_template_file()
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = bytes(tmp.read())

    response.write(file)

    return response
