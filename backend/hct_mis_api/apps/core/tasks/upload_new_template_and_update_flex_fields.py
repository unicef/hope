import logging
from io import BytesIO

from django.utils import timezone

import requests

from hct_mis_api.apps.core.flex_fields_importer import FlexibleAttributeImporter
from hct_mis_api.apps.core.kobo.api import KoboAPI
from hct_mis_api.apps.core.models import XLSXKoboTemplate

logger = logging.getLogger(__name__)


class KoboRetriableError(Exception):
    def __init__(self, xlsx_kobo_template_object):
        self.xlsx_kobo_template_object = xlsx_kobo_template_object


class UploadNewKoboTemplateAndUpdateFlexFieldsTask:
    def _save_message_status_template_id(self, xlsx_kobo_template_object, message, status, template_id=""):
        xlsx_kobo_template_object.error_description = message
        xlsx_kobo_template_object.status = status
        xlsx_kobo_template_object.template_id = template_id
        xlsx_kobo_template_object.save()

    def execute(self, xlsx_kobo_template_id) -> None:
        xlsx_kobo_template_object = XLSXKoboTemplate.objects.filter(id=xlsx_kobo_template_id).first()
        if not xlsx_kobo_template_object:
            self._save_message_status_template_id(
                xlsx_kobo_template_object, "Uploaded file is not found on the server", XLSXKoboTemplate.UNSUCCESSFUL
            )
            return

        last_valid_template = XLSXKoboTemplate.objects.latest_valid()
        if last_valid_template is None:
            template_id = ""
        else:
            template_id = last_valid_template.template_id

        try:
            file_as_bytes = BytesIO(xlsx_kobo_template_object.file.read())
            response, asset_uid = KoboAPI().create_template_from_file(
                file_as_bytes,
                xlsx_kobo_template_object,
                template_id,
            )
            response_status = response.get("status")
            response_details = response.get("detail")

            if response_status == "error" or response_details:
                error_message = response.get("messages", "") if response_status == "error" else response_details
                self._save_message_status_template_id(
                    xlsx_kobo_template_object, error_message, XLSXKoboTemplate.UNSUCCESSFUL, asset_uid
                )
                return
            else:
                flex_fields_task = FlexibleAttributeImporter()
                flex_fields_task.import_xls(xlsx_kobo_template_object.file)

            self._save_message_status_template_id(xlsx_kobo_template_object, "", XLSXKoboTemplate.SUCCESSFUL, asset_uid)
        except requests.exceptions.RequestException as e:
            logger.exception("Import template to Kobo Exception")
            if e.response is not None and 400 <= e.response.status_code < 500:
                self._save_message_status_template_id(
                    xlsx_kobo_template_object, str(e), XLSXKoboTemplate.UNSUCCESSFUL, template_id
                )
            else:
                xlsx_kobo_template_object.status = XLSXKoboTemplate.CONNECTION_FAILED
                xlsx_kobo_template_object.message = str(e)
                if xlsx_kobo_template_object.first_connection_failed_time is None:
                    xlsx_kobo_template_object.first_connection_failed_time = timezone.now()
                xlsx_kobo_template_object.save()
                raise KoboRetriableError(xlsx_kobo_template_object)
        except Exception as e:
            self._save_message_status_template_id(
                xlsx_kobo_template_object, str(e), XLSXKoboTemplate.UNSUCCESSFUL, template_id
            )
            logger.exception(e)
            raise e
