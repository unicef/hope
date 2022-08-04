import sys

from django.template.response import TemplateResponse
from django.views.debug import ExceptionReporter


def process_exception(exception, request=None):
    if not exception:
        exc_type, exception, traceback = sys.exc_info()

    reporter = ExceptionReporter(request, *sys.exc_info())

    tb_text = reporter.get_traceback_html()
    return tb_text


def render_exception(request, exception, extra_context):
    exc_type, exception, traceback = sys.exc_info()
    reporter = ExceptionReporter(request, exc_type, exception, traceback)

    context = reporter.get_traceback_data()
    context["exception"] = exception
    if extra_context:
        context.update(extra_context)
    return TemplateResponse(request, "steficon/debug.html", context)


def get_error_info(exception):
    exc_type, exception, traceback = sys.exc_info()
    reporter = ExceptionReporter(None, exc_type, exception, traceback)
    context = reporter.get_traceback_data()
    return context
