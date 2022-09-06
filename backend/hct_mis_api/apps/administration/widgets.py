from django import forms
from django.utils.safestring import mark_safe


class JsonWidget(forms.widgets.TextInput):
    template_name = "administration/json.html"

    class Media:
        # js = (
        #     settings.MEDIA_URL + 'js/rating.js',
        # )

        css = {"screen": ("administration/pygments.css",)}

    def get_email_context(self, name, value, attrs):
        import json

        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import JsonLexer

        json_object = json.loads(value)
        json_str = json.dumps(json_object, indent=4, sort_keys=True)

        context = {
            "json_pretty": mark_safe(highlight(json_str, JsonLexer(), HtmlFormatter(style="colorful", wrapcode=True))),
            # 'json_pretty': mark_safe(highlight(json_str, JsonLexer(), HtmlFormatter(wrapcode=True))),
            "widget": {
                "name": name,
                "is_hidden": self.is_hidden,
                "required": self.is_required,
                "value": self.format_value(value),
                "attrs": self.build_attrs(self.attrs, attrs),
                "template_name": self.template_name,
            },
        }
        return context
