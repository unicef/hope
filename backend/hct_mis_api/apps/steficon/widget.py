from django.forms import Textarea
from django.templatetags.static import static


class PythonEditor(Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "python-editor"

    class Media:
        css = {
            "all": (
                static("admin/steficon/codemirror/codemirror.css"),
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
        )
