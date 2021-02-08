from django.forms import Textarea


class CodeWidget(Textarea):
    template_name = "steficon/widgets/codewidget.html"

    def __init__(self, attrs=None):
        super().__init__(attrs={"class": "vLargeTextField", **(attrs or {})})
