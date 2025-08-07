class XlsxPaymentPlanBaseService:
    TITLE = "Payment Plan - Payment List"
    HEADERS = (
        "payment_id",
        "household_id",  # TODO: remove for people import/export entitlement xlsx
        "household_size",  # TODO: remove for people import/export entitlement xlsx
        "admin_level_2",
        "village",
        "collector_name",
        "payment_channel",
        "fsp_name",
        "currency",
        "entitlement_quantity",
        "entitlement_quantity_usd",
        "status",
        "national_id",
    )
