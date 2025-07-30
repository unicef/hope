SPECTACULAR_SETTINGS = {
    "TITLE": "HOPE API",
    "DESCRIPTION": "HOPE REST AOI Swagger Documentation",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
    "ENUM_NAME_OVERRIDES": {
        "PaymentPlanStatusEnum": "hct_mis_api.apps.payment.models.payment.PaymentPlan.Status",
        "PaymentStatusEnum": "hct_mis_api.apps.payment.models.payment.Payment.STATUS_CHOICE",
        "ProgramStatusEnum": "hct_mis_api.apps.program.models.Program.STATUS_CHOICE",
        "GrievanceTicketStatusEnum": "hct_mis_api.apps.grievance.models.GrievanceTicket.STATUS_CHOICES",
        "PaymentVerificationStatusEnum": "hct_mis_api.apps.payment.models.payment.PaymentVerification.STATUS_CHOICES",
    },
}
