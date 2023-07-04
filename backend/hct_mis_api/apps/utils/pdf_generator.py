from io import BytesIO
from typing import Any, Dict

from django.core.files.base import ContentFile
from django.template.loader import get_template

from weasyprint import HTML


def generate_pdf_from_html(template_name: str, data: Dict) -> Any:
    template = get_template(template_name)
    html = template.render(data)
    res = BytesIO()

    HTML(string=html).write_pdf(res, presentational_hints=True)

    pdf = ContentFile(res.getvalue())

    return pdf
