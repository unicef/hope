from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.apps.power_query"


def create_defaults():
    from .models import Formatter

    Formatter.objects.get_or_create(
        name="Dataset To HTML",
        defaults={
            "code": """
<h1>{{dataset.query.name}}</h1>
<table>
    <tr>{% for fname in dataset.data.headers %}<th>{{ fname }}</th>{% endfor %}</tr>
{% for row in dataset.data %}<tr>{% for col in row %}<td>{{ col }}</td>{% endfor %}</tr>
{% endfor %}
    </table>
""",
            "content_type": "html",
        },
    )

    Formatter.objects.get_or_create(
        name="Queryset To HTML",
        defaults={
            "code": """
<h1>{{dataset.query.name}}</h1>
<table>
    <tr><th>id</th><th>str</th></tr>
{% for row in dataset.data %}<tr>
    <td>{{ row.id }}</td>
    <td>{{ row }}</td>
    </tr>
{% endfor %}
    </table>
""",
            "content_type": "html",
        },
    )

    Formatter.objects.get_or_create(name="Dataset To XLS", defaults={"code": "", "content_type": "xls"})

    Formatter.objects.get_or_create(
        name="Queryset To JSON",
        defaults={
            "code": """
[{% for row in dataset.data %}{ "{{ row.id }}": "{{ row }}" },
{% endfor %}
]""",
            "content_type": "json",
        },
    )
