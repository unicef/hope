from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("collectstatic", interactive=False)
        call_command("migratealldb")
        call_command("generateroles")
        from adminactions.perms import create_extra_permissions

        create_extra_permissions()

        from hct_mis_api.apps.power_query.models import Formatter

        Formatter.objects.get_or_create(name='Dataset To HTML',
                                        defaults={"code": '''
<h1>{{dataset.query.name}}</h1>
<table>
    <tr>{% for fname in dataset.data.headers %}<th>{{ fname }}</th>{% endfor %}</tr>
{% for row in dataset.data %}<tr>{% for col in row %}<td>{{ col }}</td>{% endfor %}</tr>
{% endfor %}
    </table>
'''})

        Formatter.objects.get_or_create(name='Queryset To HTML',
                                        defaults={"code": '''
<h1>{{dataset.query.name}}</h1>
<table>
    <tr><th>id</th><th>str</th></tr>
{% for row in dataset.data %}<tr>
    <td>{{ row.id }}</td>
    <td>{{ row }}</td>
    </tr>
{% endfor %}
    </table>
''',
                                                  'content_type': 'html'})

        Formatter.objects.get_or_create(name='Dataset To XLS',
                                        defaults={"code": '',
                                                  'content_type': 'xls'})
