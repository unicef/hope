from django import forms
from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static


class PythonEditor(forms.Textarea):
    template_name = "steficon/widgets/codewidget.html"

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", "midnight")
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "python-editor"
        self.attrs["theme"] = theme

    class Media:
        css = {
            "all": (
                static("admin/steficon/codemirror/codemirror.css"),
                static("admin/steficon/codemirror/fullscreen.css"),
                static("admin/steficon/codemirror/midnight.css"),
                static("admin/steficon/codemirror/foldgutter.css"),
            )
        }
        js = (
            static("admin/steficon/codemirror/codemirror.js"),
            static("admin/steficon/codemirror/python.js"),
            static("admin/steficon/codemirror/fullscreen.js"),
            static("admin/steficon/codemirror/active-line.js"),
            static("admin/steficon/codemirror/foldcode.js"),
            static("admin/steficon/codemirror/foldgutter.js"),
            static("admin/steficon/codemirror/indent-fold.js"),
        )


class ContentTypeChoiceField(forms.ModelChoiceField):
    def __init__(
        self,
        *,
        empty_label="---------",
        required=True,
        widget=None,
        label=None,
        initial=None,
        help_text="",
        to_field_name=None,
        limit_choices_to=None,
        **kwargs,
    ):
        queryset = ContentType.objects.order_by("model", "app_label")
        super().__init__(
            queryset,
            empty_label=empty_label,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            to_field_name=to_field_name,
            limit_choices_to=limit_choices_to,
            **kwargs,
        )

    def label_from_instance(self, obj):
        return f"{obj.name.title()} ({obj.app_label})"
