from django.contrib.auth import get_user_model


def create_defaults() -> None:
    if get_user_model().objects.filter(is_superuser=True).first() is None:
        return
    from power_query.models import Formatter

    Formatter.objects.get_or_create(
        name="Dataset To HTML",
        defaults={
            "code": """
<h1>{{title}}</h1>
<table>
    <tr>{% for fname in dataset.data.headers %}<th>{{ fname }}</th>{% endfor %}</tr>
{% for row in dataset.data %}<tr>{% for col in row %}<td>{{ col }}</td>{% endfor %}</tr>
{% endfor %}
    </table>
"""
        },
    )

    Formatter.objects.get_or_create(
        name="Queryset To HTML",
        defaults={
            "code": """
<h1>{{title}}</h1>
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
