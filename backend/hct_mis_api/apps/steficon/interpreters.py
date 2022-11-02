import datetime
import importlib
import logging
import sys
import traceback
from builtins import __build_class__
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe

from jinja2 import Environment

from .config import config
from .exception import RuleError
from .templatetags import engine

logger = logging.getLogger(__name__)


class Interpreter:
    def __init__(self, init_string):
        self.init_string = init_string

    def validate(self):
        try:
            self.execute()
            return True
        except Exception as e:
            logger.exception(e)
            raise ValidationError(e)

    def get_result(self) -> Any:
        return config.RESULT()


class PythonFunction(Interpreter):
    label = "internal"

    @cached_property
    def code(self):
        return import_string(self.init_string)

    def execute(self, **context):
        return self.code(**context)


def call_rule(rule_id, context):
    from .models import Rule

    rule: Rule = Rule.objects.get(id=rule_id)
    return rule.execute(context)


class PythonExec(Interpreter):
    label = "Python"

    @cached_property
    def code(self):
        return compile(self.init_string, "<code>", mode="exec")

    def execute(self, context):
        gl = {
            "__builtins__": {
                "__build_class__": __build_class__,
                "__name__": __name__,
                "__import__": __import__,
                "date": datetime.date,
                # "relativedelta": dateutil.relativedelta,
                "bytearray": bytearray,
                "bytes": bytes,
                "Decimal": Decimal,
                "invoke": call_rule,
                "complex": complex,
                "dict": dict,
                "float": float,
                "frozenset": frozenset,
                "int": int,
                "list": list,
                "memoryview": memoryview,
                "range": range,
                "set": set,
                "str": str,
                "tuple": tuple,
            }
        }
        for module_name in config.BUILTIN_MODULES:
            try:
                mod = importlib.import_module(module_name)
                gl["__builtins__"][module_name] = mod
            except Exception as e:
                logger.exception(e)

        pts = self.get_result()
        locals_ = dict()
        locals_["context"] = context
        locals_["result"] = pts
        try:
            exec(self.init_string, gl, locals_)
        except SyntaxError as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = err.lineno
            raise RuleError(
                rule=self,
                error_class=error_class,
                detail=detail,
                line_number=line_number,
                traceback=None,
            )
        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]
            raise RuleError(
                rule=self,
                error_class=error_class,
                detail=detail,
                line_number=line_number,
                traceback=traceback,
            )
        else:
            return pts

    def validate(self):
        errors = []
        for forbidden in [
            "__import__",
            "raw",
            "connection",
            "import",
            "delete",
            "save",
            "eval",
            "exec",
        ]:
            if forbidden in self.init_string:
                errors.append("Code contains an invalid statement '{}'".format(forbidden))
        if errors:
            raise ValidationError(errors)
        try:
            compile(self.init_string, "<code>", mode="exec")
            return True
        except Exception as e:
            logger.exception(e)
            tb = traceback.format_exc(limit=-1)
            msg = tb.split('<code>", ')[-1]
            raise ValidationError(mark_safe(msg))


def get_env(**options) -> Environment:
    env = Environment(**options)
    env.filters.update(
        {
            "adults": engine.adults
            # 'url': reverse,
        }
    )
    return env


interpreters = [
    PythonExec,
    # PythonFunction,
]
mapping = {a.label.lower(): a for a in interpreters}
