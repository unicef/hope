from django.urls import reverse_lazy

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "hct_mis_api.api.utils.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "SECURE_SSL_REDIRECT": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "HOPE API",
    "DESCRIPTION": "HOPE REST AOI Swagger Documentation",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

SWAGGER_SETTINGS = {
    "LOGOUT_URL": reverse_lazy("logout"),
    "LOGIN_URL": "/",
    "SECURITY_DEFINITIONS": {"DRF Token": {"type": "apiKey", "name": "Authorization", "in": "header"}},
}
