from django.forms import Textarea


class CodeWidget(Textarea):
    template_name = "power_query/widgets/codewidget.html"

    class Media:
        css = {
            "all": (
                'admin/power_query/code.css',
            )
        }
        js = (
            "admin/power_query/edit_area/edit_area_loader.js",
        )

    def __init__(self, attrs=None):
        super().__init__(attrs={"class": "vLargeTextField", **(attrs or {})})

    def build_attrs(self, base_attrs, extra_attrs=None):
        base_attrs["class"] = "vLargeTextField codepress generic linenumbers-on"
        return super().build_attrs(base_attrs, extra_attrs)
