from django.forms import Textarea


class CodeWidget(Textarea):
    template_name = "steficon/widgets/codewidget.html"

    class Media:
        css = {
            "all": (
                # 'admin/steficon/editor/edit_area.css',
            )
        }
        js = (
            # 'admin/steficon/editor/edit_area_full.js',
            "admin/steficon/edit_area/edit_area_loader.js",
            # 'admin/steficon/editor/edit_area.js',
            # 'admin/steficon/editor/regexp.js',
            # 'admin/steficon/editor/autocompletion.js',
            # 'admin/steficon/codepress/engines/gecko.js',
            # 'admin/steficon/codepress/codepress.js',
            # 'admin/steficon/codepress/languages/generic.js',
        )

    def __init__(self, attrs=None):
        super().__init__(attrs={"class": "vLargeTextField", **(attrs or {})})

    def build_attrs(self, base_attrs, extra_attrs=None):
        base_attrs["class"] = "vLargeTextField codepress generic linenumbers-on"
        return super().build_attrs(base_attrs, extra_attrs)
