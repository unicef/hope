import sys
from typing import Dict, Optional, TYPE_CHECKING

from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.views.debug import ExceptionReporter

if TYPE_CHECKING:
    from django.http import HttpRequest


def process_exception(exception: BaseException, request: Optional[HttpRequest] = None) -> str:
    if not exception:
        exc_type, exception, traceback = sys.exc_info()

    reporter = ExceptionReporter(request, *sys.exc_info())

    tb_text = reporter.get_traceback_html()
    return tb_text


def render_exception(request: HttpRequest, exception: BaseException, extra_context: Dict) -> TemplateResponse:
    exc_type, exception, traceback = sys.exc_info()
    reporter = ExceptionReporter(request, exc_type, exception, traceback)

    context = reporter.get_traceback_data()
    context["exception"] = exception
    if extra_context:
        context.update(extra_context)
    return TemplateResponse(request, "steficon/debug.html", context)


def get_error_info(exception: BaseException) -> Dict:
    exc_type, exception, traceback = sys.exc_info()
    reporter = ExceptionReporter(None, exc_type, exception, traceback)
    context = reporter.get_traceback_data()
    return context
