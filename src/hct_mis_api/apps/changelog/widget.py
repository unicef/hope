from django import forms


class HTMLEditor(forms.Textarea):
    template_name = "changelog/widgets/editor.html"

    class Media:
        css = {"all": ("https://unpkg.com/easymde/dist/easymde.min.css",)}
        js = ("https://unpkg.com/easymde/dist/easymde.min.js",)
