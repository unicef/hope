from django.dispatch import Signal

payment_plan_approved = Signal()
payment_plan_authorized = Signal()
payment_delivery_export_passwords_generated = Signal()
payment_plan_group_payment_list_xlsx_generated = Signal()
payment_plan_payment_list_pdf_generated = Signal()
payment_plan_payment_list_xlsx_generated = Signal()
payment_plan_reconciliation_overdue = Signal()
payment_plan_released = Signal()
payment_plan_sent_for_approval = Signal()
payment_verification_plan_xlsx_generated = Signal()
western_union_report_generated = Signal()
