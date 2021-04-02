#  :copyright: Copyright (c) 2018-2020. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, October 2020
from environ import Env


def parse_emails(value):
    admins = value.split(",")
    v = [(a.split("@")[0].strip(), a.strip()) for a in admins]
    return v


DEFAULTS = {
    "ADMINS": (parse_emails, ""),
    "ALLOWED_HOSTS": (list, ""),
    "AZURE_CLIENT_ID": (str, ""),
    "AZURE_CLIENT_SECRET": (str, ""),
    "AZURE_TENANT_KEY": (str, ""),
    "CACHE_URL": (Env.cache, "dummycache://"),
    "CELERY_BROKER_URL": (str, "redis://redis/0"),
    "CELERY_RESULT_BACKEND": (str, "redis://redis/0"),
    "CELERY_TASK_ALWAYS_EAGER": (bool, False),
    "CONSTANCE_REDIS_CONNECTION": (str, "redis://redis/0"),
    "DATABASE_URL": (str, "psql://postgres:@127.0.0.1:5432/sos"),
    "DATABASE_URL_HUB_CA": (str, "psql://postgres:@127.0.0.1:5432/sos"),
    "DATABASE_URL_HUB_ERP": (str, "psql://postgres:@127.0.0.1:5432/sos"),
    "DATABASE_URL_HUB_MIS": (str, "psql://postgres:@127.0.0.1:5432/sos"),
    "DATABASE_URL_HUB_REGISTRATION": (str, "psql://postgres:@127.0.0.1:5432/sos"),
    "DATAMART_PASSWORD": (str, ""),
    "DATAMART_URL": (str, "https://datamart-dev.unicef.io"),
    "DATAMART_USER": (str, ""),
    "DATA_VOLUME": (str, "/data"),
    "DEBUG": (bool, False),
    "DEFAULT_FROM_EMAIL": (str, "HCT-MIS Stage <noreply@hct-mis.org>"),
    "DJANGO_ALLOWED_HOSTS": (list, "*"),
    "DOMAIN": (str, "localhost"),
    "ELASTICSEARCH_HOST": (str, "elasticsearch:9200"),
    "EMAIL_SUBJECT_PREFIX": (str, "[HOPE]"),
    "EMAIL_URL": (Env.email_url, "smtp://user@:password@localhost:25"),
    "EMAIL_USE_LOCALTIME": (bool, False),
    "GIT_VERSION": (str, "UNKNOWN"),
    "HCT_MIS_FRONTEND_HOST": (str, "*"),
    "HCT_MIS_UPLOADS_PATH": (str, "*"),
    "KOBO_MASTER_API_TOKEN": (str, "https://datamart-dev.unicef.io"),
    "MEDIA_URL": (str, "media/"),
    "RAPID_PRO_URL": (str, "https://rapidpro.io"),
    "SANCTION_LIST_CC_MAIL": (str, "dfam-cashassistance@unicef.org"),
    "SECRET_KEY": (str, ""),
    "SENTRY_DSN": (str, ""),
    "SENTRY_URL": (str, "https://excubo.unicef.io/sentry/hct-mis-stg/"),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (bool, True),
    "STATIC_URL": (str, "static/"),
    "STORAGE_AZURE_ACCOUNT_NAME": (str, ""),
    "STORAGE_AZURE_ACCOUNT_KEY": (str, ""),
    "STORAGE_DEFAULT": "hct_mis_api.apps.core.storage.AzureMediaStorage",
    "STORAGE_STATICFILES": "hct_mis_api.apps.core.storage.AzureStaticStorage",
    "TEST_USERS": (parse_emails, ""),
}
env = Env(**DEFAULTS)
