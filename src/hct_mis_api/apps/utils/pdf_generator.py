from typing import Any

from django.template.loader import get_template

from weasyprint import HTML


def generate_pdf_from_html(template_name: str, data: dict) -> Any:
    template = get_template(template_name)
    html_content = template.render(data)

    return HTML(string=html_content).write_pdf()
