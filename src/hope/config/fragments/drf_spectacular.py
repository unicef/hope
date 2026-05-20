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
        "PaymentPlanStatusEnum": "hope.models.payment_plan.PaymentPlan.Status",
        "PaymentStatusEnum": "hope.models.payment.Payment.STATUS_CHOICE",
        "ProgramStatusEnum": "hope.models.program.Program.STATUS_CHOICE",
        "GrievanceTicketStatusEnum": "hope.apps.grievance.models.GrievanceTicket.STATUS_CHOICES",
        "PaymentVerificationStatusEnum": "hope.models.payment_verification.PaymentVerification.STATUS_CHOICES",
    },
}
