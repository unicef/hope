from django import forms
from django.templatetags.static import static


class HTMLEditor(forms.Textarea):
    template_name = "changelog/widgets/editor.html"

    class Media:
        css = {"all": (static("admin/changelog/easymde/easymde.min.css"),)}
        js = (static("admin/changelog/easymde/easymde.min.js"),)
