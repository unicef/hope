import json
from collections import defaultdict
from typing import Union

from django.core.files import File
from django.core.management import BaseCommand
from django.db.models import F

from hct_mis_api.apps.core.kobo.api import KoboAPI
from hct_mis_api.apps.core.kobo.common import (
    KOBO_FORM_INDIVIDUALS_COLUMN_NAME,
    get_field_name,
)
from hct_mis_api.apps.core.utils import rename_dict_keys
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import ImportData, ImportedDocument
from hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create import (
    RdiKoboCreateTask,
)


def _get_file(attachments, value, business_area_slug) -> Union[File, str]:
    # TODO: refactor
    download_url = ""
    for attachment in attachments:
        filename = attachment.get("filename", "")
        current_download_url = attachment.get("download_url", "")
        if filename.endswith(value):
            download_url = current_download_url.replace("?format=json", "")

    if not download_url:
        return download_url

    api = KoboAPI(business_area_slug)
    image_bytes = api.get_attached_file(download_url)
    file = File(image_bytes, name=value)

    return file


def fix_document_photos() -> None:
    imported_documents = (
        ImportedDocument.objects.filter(
            photo="", individual__registration_data_import__import_data__data_type=ImportData.JSON
        )
        .annotate(hct_id=F("individual__registration_data_import__hct_id"))
        .annotate(import_data_id=F("individual__registration_data_import__import_data"))
    )

    documents_to_update = []
    imported_documents_to_update = []
    for imported_document in imported_documents:
        document_number = imported_document.document_number
        file = None

        rdi = RegistrationDataImport.objects.filter(id=imported_document.hct_id).first()
        if not rdi:
            print(f"Not found RegistrationDataImport object for Imported Document: {imported_document.id}")
            continue
        if not rdi.pull_pictures:
            continue

        try:
            json_file = ImportData.objects.get(id=imported_document.import_data_id).file.read()
        except Exception as e:
            print(f"Error get or read json file for Imported Document: {imported_document.id}. {e}")
            continue

        for household in rename_dict_keys(json.loads(json_file), get_field_name):
            if file:
                break

            for hh_field, hh_value in household.items():
                if file:
                    break
                if hh_field == KOBO_FORM_INDIVIDUALS_COLUMN_NAME:
                    for individual in hh_value:
                        individual_docs_and_identities = defaultdict(dict)
                        for i_field, i_value in individual.items():
                            if i_field in RdiKoboCreateTask.DOCS_AND_IDENTITIES_FIELDS:
                                if i_field.endswith("_type_i_c") or i_field.endswith("_issuer_i_c"):
                                    continue
                                elif i_field.endswith("_photo_i_c"):
                                    value_key = "photo"
                                else:
                                    value_key = "number"

                                individual_docs_and_identities[value_key] = i_value

                        if individual_docs_and_identities.get("number") == document_number:
                            value = individual_docs_and_identities.get("photo", "")
                            business_area_slug = (
                                imported_document.individual.registration_data_import.business_area_slug
                            )
                            file = _get_file(household.get("_attachments", []), value, business_area_slug)
                            break
                            # stop looping if file is not null
        if file:
            imported_document.photo = file
            imported_documents_to_update.append(imported_document)

            document = Document.objects.filter(
                individual__registration_data_import__id=imported_document.hct_id,
                document_number=document_number,
                photo="",
            ).first()

            if document:
                document.photo = file
                documents_to_update.append(document)
            print(f"Fixed Imported Document: {imported_document.id}")
        else:
            print(f"Not found photo for Imported Document: {imported_document.id}")

    Document.objects.bulk_update(documents_to_update, ["photo"], 1000)
    ImportedDocument.objects.bulk_update(imported_documents_to_update, ["photo"], 1000)


class Command(BaseCommand):
    help = "Fix document photos in Individuals existing data"

    def handle(self, *args, **options):
        fix_document_photos()
        self.stdout.write("Individuals photos fixed")
