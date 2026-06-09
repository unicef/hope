import sys

from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.views.debug import ExceptionReporter


def process_exception(exception: BaseException | None, request: HttpRequest | None = None) -> str | None:
    if not exception:
        exc_type, exception, traceback = sys.exc_info()

    reporter = ExceptionReporter(request, *sys.exc_info())

    return reporter.get_traceback_html()


def render_exception(request: HttpRequest, exception: BaseException | None, extra_context: dict) -> TemplateResponse:
    exc_type, exception, traceback = sys.exc_info()
    reporter = ExceptionReporter(request, exc_type, exception, traceback)

    context = reporter.get_traceback_data()
    context["exception"] = exception
    if extra_context:
        context.update(extra_context)
    return TemplateResponse(request, "steficon/debug.html", context)


def get_error_info(exception: BaseException | None) -> dict:
    exc_type, exception, traceback = sys.exc_info()
    reporter = ExceptionReporter(None, exc_type, exception, traceback)
    return reporter.get_traceback_data()
