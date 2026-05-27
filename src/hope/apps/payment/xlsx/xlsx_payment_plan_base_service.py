class XlsxPaymentPlanBaseService:
    TITLE = "Payment Plan - Payment List"
    COLUMN_PAYMENT_ID = "payment_id"
    COLUMN_ENTITLEMENT_QUANTITY = "entitlement_quantity"
    HEADERS = (
        COLUMN_PAYMENT_ID,
        "household_id",
        "individual_id",
        "collector_id",
        "household_size",
        "admin_level_2",
        "village",
        "collector_name",
        "payment_channel",
        "fsp_name",
        "currency",
        COLUMN_ENTITLEMENT_QUANTITY,
        "entitlement_quantity_usd",
        "status",
        "national_id",
    )
