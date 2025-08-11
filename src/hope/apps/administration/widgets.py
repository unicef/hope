from typing import Any

from django import forms


class JsonWidget(forms.widgets.TextInput):
    template_name = "administration/json.html"

    class Media:
        css = {"screen": ("administration/pygments.css",)}

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict:
        import json

        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import JsonLexer

        json_object = json.loads(value)
        json_str = json.dumps(json_object, indent=4, sort_keys=True)

        return {
            "json_pretty": highlight(json_str, JsonLexer(), HtmlFormatter(style="colorful", wrapcode=True)),
            "widget": {
                "name": name,
                "is_hidden": self.is_hidden,
                "required": self.is_required,
                "value": self.format_value(value),
                "attrs": self.build_attrs(self.attrs, attrs),
                "template_name": self.template_name,
            },
        }
