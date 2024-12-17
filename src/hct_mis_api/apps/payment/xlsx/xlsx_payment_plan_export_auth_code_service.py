# AB#225622
from celery.bin.control import status

from hct_mis_api.apps.payment.models import Payment

from hope_smart_export import ExportAsXls


# Allow user to download MTCNs/FSP auth codes
# Define new permission to download records with AUTH Code
# Allow user to define an FSP template to export these columns
# Include 'FSP AUTH CODE' field within FSP template definition at admin
#
# Enable the 'Export' button/feature ONLY after all payment records status changed to 'Transferred to FSP' (to ensure that there are MTCNs/ AUTH CODEs generated)
# by current implementation, the export can be done only once.
# the exported file is encrypted with a password, and the password is shared separately in another email.


class XLSXPaymentPlanExportAuthCodeService:

    @staticmethod
    def export_xlsx(payment_plan_id: str, xlsx_template_id: str, user_id: str):
        for payment in Payment.objects.all():
            payment.fsp_auth_code
            continue

        # use ExportAsXls

# for payment in Payment Plan
# if payment status == Payment.STATUS_SENT_TO_FSP
#    payment.fsp_auth_code

# use user selected template

# add password and send link to user

# send other email with password
