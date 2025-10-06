REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "hope.apps.core.api.pagination.NoCountLimitOffsetPagination",
    "PAGE_SIZE": 50,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "hope.api.utils.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "SECURE_SSL_REDIRECT": True,
}
