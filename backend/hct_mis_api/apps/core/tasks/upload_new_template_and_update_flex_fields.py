from hct_mis_api.apps.core.flex_fields_importer import FlexibleAttributeImporter
from hct_mis_api.apps.core.kobo.api import KoboAPI
from io import BytesIO

from hct_mis_api.apps.core.models import XLSXKoboTemplate


class UploadNewKoboTemplateAndUpdateFlexFieldsTask:
    def _save_message_and_update_status(self, xlsx_kobo_template_object, message, status):
        xlsx_kobo_template_object.error_description = message
        xlsx_kobo_template_object.status = status
        xlsx_kobo_template_object.save()

    def execute(self, xlsx_kobo_template_id):
        xlsx_kobo_template_object = XLSXKoboTemplate.objects.filter(id=xlsx_kobo_template_id).first()
        if not xlsx_kobo_template_object:
            self._save_message_and_update_status(
                xlsx_kobo_template_object, "Uploaded file is not found on the server", XLSXKoboTemplate.UNSUCCESSFUL
            )
            return

        try:
            file_as_bytes = BytesIO(xlsx_kobo_template_object.file.read())
            response = KoboAPI("afghanistan").create_survey_from_file(file_as_bytes)
            response_status = response.get("status")
            response_details = response.get("detail")

            if response_status == "error" or response_details:
                error_message = response.get("messages", "") if response_status == "error" else response_details
                self._save_message_and_update_status(
                    xlsx_kobo_template_object, error_message, XLSXKoboTemplate.UNSUCCESSFUL
                )
                return
            else:
                flex_fields_task = FlexibleAttributeImporter()
                flex_fields_task.import_xls(xlsx_kobo_template_object.file.path)

            self._save_message_and_update_status(xlsx_kobo_template_object, "", XLSXKoboTemplate.SUCCESSFUL)

        except Exception as e:
            self._save_message_and_update_status(xlsx_kobo_template_object, str(e), XLSXKoboTemplate.UNSUCCESSFUL)
            raise e
