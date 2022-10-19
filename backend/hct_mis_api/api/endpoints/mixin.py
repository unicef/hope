import base64
import logging
from dataclasses import dataclass

from django.core.files.uploadedfile import SimpleUploadedFile

from hct_mis_api.apps.household.models import (
    HEAD,
    NON_BENEFICIARY,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)

logger = logging.getLogger(__name__)


def get_photo_from_stream(stream):
    if stream:
        base64_img_bytes = stream.encode("utf-8")
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        return SimpleUploadedFile("photo.png", decoded_image_data, content_type="image/png")

    return None


@dataclass
class Totals:
    individuals: int
    households: int


class HouseholdUploadMixin:
    def save_document(self, member, doc):
        ImportedDocument.objects.create(
            document_number=doc["document_number"],
            photo=get_photo_from_stream(doc.get("image", None)),
            doc_date=doc["doc_date"],
            individual=member,
            country=doc["country"],
            type=ImportedDocumentType.objects.get(type=doc["type"]),
        )

    def save_member(
        self, rdi: RegistrationDataImportDatahub, hh: ImportedHousehold, member_data: dict
    ) -> ImportedIndividual:
        documents = member_data.pop("documents", [])
        member_of = None
        if member_data["relationship"] not in (RELATIONSHIP_UNKNOWN, NON_BENEFICIARY):
            member_of = hh
        role = member_data.pop("role", None)
        ind = ImportedIndividual.objects.create(household=member_of, registration_data_import=rdi, **member_data)
        for doc in documents:
            self.save_document(ind, doc)
        if member_data["relationship"] == HEAD:
            hh.head_of_household = ind
            hh.save()
        if role == ROLE_PRIMARY:
            hh.individuals_and_roles.create(individual=ind, role=ROLE_PRIMARY)
        elif role == ROLE_ALTERNATE:
            hh.individuals_and_roles.create(individual=ind, role=ROLE_ALTERNATE)
        return ind

    def save_households(self, rdi: RegistrationDataImportDatahub, households_data: list[dict]):
        totals = Totals(0, 0)
        for household_data in households_data:
            totals.households += 1
            members: list[dict] = household_data.pop("members")
            hh = ImportedHousehold.objects.create(registration_data_import=rdi, **household_data)
            for member_data in members:
                self.save_member(rdi, hh, member_data)
                totals.individuals += 1
        return totals
