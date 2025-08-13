import os
from datetime import datetime

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files.base import ContentFile

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.core.services.ftp_client import FTPClient
from hct_mis_api.apps.payment.models import PaymentPlan


class WesternUnionFTPClient(FTPClient):
    HOST = os.getenv("FTP_WESTERN_UNION_SERVER")
    PORT = int(os.getenv("FTP_WESTERN_UNION_PORT"))
    USERNAME = os.getenv("FTP_WESTERN_UNION_USERNAME")
    PASSWORD = os.getenv("FTP_WESTERN_UNION_PASSWORD")

    def print_files(self) -> None:
        files = self.list_files_w_attrs()
        for attr in files:
            print(
                {
                    "filename": attr.filename,
                    "modified": datetime.fromtimestamp(attr.st_mtime),
                }
            )

    def process_files_since(self, date_from: datetime) -> None:
        files = [f for f in self.list_files_w_attrs() if datetime.fromtimestamp(f.st_mtime) >= date_from]
        # filter by some name pattern?
        for f in files:
            file_like = self.download(f.filename)
            content_file = ContentFile(file_like.read(), name=f.filename)
            self.process_file(content_file, f.filename)

    def process_file(self, content_file: ContentFile, filename: str) -> None:
        # iterate over each line and get payment unicef id
        # get payment plan instance from payment
        # check if PP already doesn't have an invoice file (can it have more than one file?)

        file_temp = FileTemp.objects.create(
            # object_id=payment_plan.pk,
            # content_type=get_content_type_for_model(payment_plan),
            file=content_file,
        )
        file_temp.file.save(filename, content_file)

        # payment_plan.ftp_invoice_file = file_temp
        # obj.save()
        # process records data (amount, fee)
