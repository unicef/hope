class XlsxPaymentListBaseService:
    TITLE = "Payment List"
    # Templates exported before the payment list rename carry this sheet title.
    LEGACY_TITLES = ("Payment Plan - Payment List",)
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

    @classmethod
    def payment_sheet_name(cls, sheet_names: list[str]) -> str | None:
        return next((name for name in (cls.TITLE, *cls.LEGACY_TITLES) if name in sheet_names), None)
