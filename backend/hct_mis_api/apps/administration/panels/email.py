from typing import Any, Union
from smart_admin.console.email import (
    concurrent,
    logger,
    messages,
    render,
    settings,
    timezone,
)

from hct_mis_api.apps.utils.security import is_root
from django.http import HttpRequest


def masker(value: Any, request: HttpRequest) -> Union[Any, str]:
    if is_root(request):
        return value
    return "****"


def email(self, request, extra_context=None):
    context = self.each_context(request)
    context["title"] = "Test Email"
    context["smtp"] = {
        "EMAIL_BACKEND": settings.EMAIL_BACKEND,
        "EMAIL_HOST": settings.EMAIL_HOST,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_HOST_PASSWORD": masker(settings.EMAIL_HOST_PASSWORD, request),
        "EMAIL_HOST_USER": settings.EMAIL_HOST_USER,
        "EMAIL_USE_SSL": settings.EMAIL_USE_SSL,
        "EMAIL_USE_TLS": settings.EMAIL_USE_TLS,
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
    }
    results = {}
    logs = []
    if request.method == "POST":
        try:
            from django.core.mail import get_connection

            conn = get_connection()
            context["connection"] = conn
            from django.core.mail import send_mail

            kwargs = {
                "subject": "Send email test: 'django.core.mail.send_mail'",
                "from_email": None,
                "message": "Test send email using raw 'django.core.mail.send_mail'",
                "recipient_list": [request.user.email],
            }
            logs.append([timezone.now(), "Thread started"])
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(send_mail, **kwargs)
                exc = future.exception()
                if exc:
                    messages.add_message(request, messages.ERROR, f"{exc.__class__.__name__}: {exc}")
                    logs.append([timezone.now(), f"Thread error {exc}"])
                else:
                    return_value = future.result()
                    logs.append([timezone.now(), f"Thread completed {return_value}"])
                    if return_value == 1:
                        messages.add_message(request, messages.SUCCESS, f"Email sent to {request.user.email}")
        except Exception as e:
            logger.exception(e)
            messages.add_message(request, messages.ERROR, f"{e.__class__.__name__}: {e}")
    context["logs"] = logs
    context["results"] = results
    return render(request, "smart_admin/panels/email.html", context)
