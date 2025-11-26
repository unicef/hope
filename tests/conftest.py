import os

COMMON_SETTINGS = {
    "DEBUG": True,
    "ALLOWED_HOSTS": [
        "localhost",
        "127.0.0.1",
        "10.0.2.2",
        os.getenv("DOMAIN", ""),
    ],
    "CELERY_TASK_ALWAYS_EAGER": True,
    "ELASTICSEARCH_INDEX_PREFIX": "test_",
    "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
    "CATCH_ALL_EMAIL": [],
    "DEFAULT_EMAIL": "testemail@email.com",
    "EXCHANGE_RATE_CACHE_EXPIRY": 0,
    "USE_DUMMY_EXCHANGE_RATES": True,
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": True,
    "CSRF_COOKIE_SECURE": False,
    "CSRF_COOKIE_HTTPONLY": False,
    "SESSION_COOKIE_SECURE": False,
    "SESSION_COOKIE_HTTPONLY": True,
    "SECURE_HSTS_SECONDS": False,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "SECURE_REFERRER_POLICY": "same-origin",
    "CACHE_ENABLED": False,
    "TESTS_ROOT": os.getenv("TESTS_ROOT"),
}

LOGGERS = {
    "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
    "registration_datahub.tasks.deduplicate": {
        "handlers": ["default"],
        "level": "INFO",
        "propagate": True,
    },
    "sanction_list.tasks.check_against_sanction_list_pre_merge": {
        "handlers": ["default"],
        "level": "INFO",
        "propagate": True,
    },
    "elasticsearch": {
        "handlers": ["default"],
        "level": "CRITICAL",
        "propagate": True,
    },
    "elasticsearch-dsl-django": {
        "handlers": ["default"],
        "level": "CRITICAL",
        "propagate": True,
    },
    "hope.apps.registration_datahub.tasks.deduplicate": {
        "handlers": ["default"],
        "level": "CRITICAL",
        "propagate": True,
    },
    "hope.apps.core.tasks.upload_new_template_and_update_flex_fields": {
        "handlers": ["default"],
        "level": "CRITICAL",
        "propagate": True,
    },
}
