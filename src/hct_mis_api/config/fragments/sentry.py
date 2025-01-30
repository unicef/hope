import logging

from hct_mis_api.config.env import env

SENTRY_DSN = env("SENTRY_DSN")
SENTRY_URL = env("SENTRY_URL")
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT")
SENTRY_ENABLE_TRACING = env("SENTRY_ENABLE_TRACING")

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

    from hct_mis_api import get_full_version
    from hct_mis_api.apps.utils.sentry import SentryFilter

    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,  # Capture info and above as breadcrumbs  # Send errors as events
    )
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            sentry_logging,
            CeleryIntegration(),
        ],
        release=get_full_version(),
        enable_tracing=SENTRY_ENABLE_TRACING,
        traces_sample_rate=1.0,
        send_default_pii=True,
        ignore_errors=[
            "ValidationError",
            "PermissionDenied",
            "Http404",
            "AuthCanceled",
            "TokenNotProvided",
        ],
        before_send=SentryFilter().before_send,
        environment=SENTRY_ENVIRONMENT,
    )
    ignore_logger("graphql.execution.utils")
