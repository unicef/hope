import datetime
import importlib
import logging
import sys
import traceback
from builtins import __build_class__
from decimal import Decimal
from typing import Any, Dict, List, Type
from uuid import UUID

from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from jinja2 import Environment

from hct_mis_api.apps.steficon.config import config
from hct_mis_api.apps.steficon.exception import RuleError
from hct_mis_api.apps.steficon.templatetags import engine

logger = logging.getLogger(__name__)


class Interpreter:
    def __init__(self, init_string: str) -> None:
        self.init_string = init_string

    def validate(self) -> bool:
        try:
            self.execute()
            return True
        except Exception as e:
            logger.exception(e)
            raise ValidationError(str(e))

    def get_result(self) -> Any:
        return config.RESULT()


def call_rule(rule_id: UUID, context: Dict) -> Any:
    from hct_mis_api.apps.steficon.models import Rule

    rule: Rule = Rule.objects.get(id=rule_id)
    return rule.execute(context)


class PythonExec(Interpreter):
    label = "Python"

    @cached_property
    def code(self) -> Any:
        return compile(self.init_string, "<code>", mode="exec")

    def execute(self, context: Dict) -> Any:
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

    def validate(self) -> bool:
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


def get_env(**options: Any) -> Environment:
    env = Environment(**options)
    env.filters.update({"adults": engine.adults})
    return env


interpreters: List[Type[Interpreter]] = [
    PythonExec,
]
mapping: Dict[str, Type[Interpreter]] = {a.label.lower(): a for a in interpreters}
