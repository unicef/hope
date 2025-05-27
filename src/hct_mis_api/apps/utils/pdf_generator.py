from typing import Any, Dict

from django.template.loader import get_template

from weasyprint import HTML


def generate_pdf_from_html(template_name: str, data: Dict) -> Any:
    template = get_template(template_name)
    html_content = template.render(data)

    pdf_file = HTML(string=html_content).write_pdf()

    return pdf_file
