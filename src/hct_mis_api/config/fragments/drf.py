REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "hct_mis_api.apps.core.api.pagination.NoCountLimitOffsetPagination",
    "PAGE_SIZE": 50,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "hct_mis_api.api.utils.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "SECURE_SSL_REDIRECT": True,
}
