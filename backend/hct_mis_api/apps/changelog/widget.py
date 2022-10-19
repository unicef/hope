from django.templatetags.static import static
from django import forms


class HTMLEditor(forms.Textarea):
    template_name = "changelog/widgets/editor.html"

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", "snow")
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "formatter-editor"
        self.attrs["theme"] = theme

    class Media:
        css = {
            "all": (
                static("admin/changelog/quill/quill.core.css"),
                static("admin/changelog/quill/quill.snow.css"),
            )
        }
        js = (
            static("admin/changelog/quill/quill.core.js"),
            static("admin/changelog/quill/quill.min.js"),
        )
