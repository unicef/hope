from decimal import Decimal
from unittest.mock import Mock

from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from steficon.score import Score
from steficon.templatetags import engine
from household.models import Household


class Interpreter:
    def __init__(self, init_string):
        self.init_string = init_string

    def validate(self):
        try:
            self.execute(hh=Household.objects.first())
        except Exception as e:
            raise ValidationError(e)

class PythonFunction(Interpreter):
    label = 'internal'

    @cached_property
    def code(self):
        return import_string(self.init_string)

    def execute(self, **context):
        return self.code(**context)



class PythonExec(Interpreter):
    label = 'Python'

    @cached_property
    def code(self):
        return compile(self.init_string, "<code>", mode='exec')

    def execute(self, **context):
        gl = {'__builtins__': {}}
        pts = Score()
        locals_ = dict(context)
        locals_['pts'] = pts
        exec(self.code, gl, locals_)
        return pts.total()

    def validate(self):
        errors = []
        for forbidden in ['__import__', 'delete', 'save', 'eval', 'exec']:
            if forbidden in self.init_string:
                errors.append("Code contains an invalid statement '%s'" % forbidden)
        if errors:
            raise ValidationError(errors)

        return super().validate()


from jinja2 import Template, Environment


# from jinja2 import environment

def get_env(**options) -> Environment:
    env = Environment(**options)
    env.filters.update({
        'adults': engine.adults
        # 'url': reverse,
    })
    return env


# environment.DEFAULT_FILTERS['md5'] = lambda s: md5(s.encode('utf-8'))
# environment.DEFAULT_FILTERS['hexdigest'] = lambda s: s.hexdigest()
# environment.DEFAULT_FILTERS['urlencode'] = urlencode
# environment.DEFAULT_FILTERS['slugify'] = slugify

class Jinja(Interpreter):
    label = 'Jinja2'

    @cached_property
    def code(self):
        return get_env().from_string(self.init_string)

    def execute(self, **context):
        pts = Score()
        context['pts'] = pts
        output = self.code.render(**context)
        return Decimal(output.strip())


interpreters = [Jinja, PythonFunction, PythonExec]
mapping = {a.label.lower(): a for a in interpreters}
