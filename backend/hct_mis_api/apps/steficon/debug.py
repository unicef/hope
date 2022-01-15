import sys

from django.template import Context
from django.template.response import TemplateResponse
from django.views.debug import ExceptionReporter


def process_exception(exception, request=None):
    if not exception:
        exc_type, exception, traceback = sys.exc_info()

    reporter = ExceptionReporter(request, *sys.exc_info())

    tb_text = reporter.get_traceback_html()
    class_name = exception.__class__.__name__

    # if request:
    #     url = request.build_absolute_uri()
    #     user = getattr(request, 'user', None)
    #     data = dict(
    #         META=request.META,
    #         POST=request.POST,
    #         GET=request.GET,
    #         COOKIES=request.COOKIES,
    #     )
    # else:
    #     url = 'N/A'
    #     user = 'N/A'
    #     data = dict()
    return tb_text
    # defaults = dict(
    #     class_name=class_name,
    #     message=str(exception),
    #     url=url,
    #     server_name=server_name,
    #     traceback=tb_text,
    #     username=str(user)
    # )
    #
    # try:
    #     err = Error.objects.create(**defaults)
    #     if message_user and request:
    #         err.message_user(request, str(exception))
    #     return err
    # except Exception as exc:  # pragma: no cover
    #     try:
    #         logger.critical(f"""Unable to log exception:


# Reason: {exc}
#
# {str(exception)}
#
# """)
#             logger.exception(exception)
#         except Exception as exc:
#             warnings.warn(u'Unable to process log entry: %s' % (exc,))
#


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
