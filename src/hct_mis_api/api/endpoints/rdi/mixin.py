import base64
import logging
from dataclasses import dataclass

from django.core.files.uploadedfile import SimpleUploadedFile

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    HEAD,
    NON_BENEFICIARY,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)


def get_photo_from_stream(stream: str | None) -> SimpleUploadedFile | None:
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
    def save_document(self, member: PendingIndividual, doc: dict) -> None:
        PendingDocument.objects.create(
            document_number=doc["document_number"],
            photo=get_photo_from_stream(doc.get("image")),
            individual=member,
            country=Country.objects.get(iso_code2=doc["country"]),
            type=DocumentType.objects.get(key=doc["type"]),
            program=member.program,
        )

    def save_member(self, rdi: RegistrationDataImport, hh: PendingHousehold, member_data: dict) -> PendingIndividual:
        documents = member_data.pop("documents", [])
        member_of = None
        if member_data["relationship"] not in (RELATIONSHIP_UNKNOWN, NON_BENEFICIARY):
            member_of = hh
        member_data["flex_fields"] = populate_pdu_with_null_values(rdi.program, member_data.get("flex_fields"))
        role = member_data.pop("role", None)
        ind = PendingIndividual.objects.create(
            household=member_of,
            program=rdi.program,
            registration_data_import=rdi,
            business_area=rdi.business_area,
            **member_data,
        )
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

    def save_households(self, rdi: RegistrationDataImport, households_data: list[dict]) -> Totals:
        totals = Totals(0, 0)
        for household_data in households_data:
            totals.households += 1
            members: list[dict] = household_data.pop("members")
            if country := household_data.get("country"):
                household_data["country"] = Country.objects.get(iso_code2=country)

            if country_origin := household_data.get("country_origin"):
                household_data["country_origin"] = Country.objects.get(iso_code2=country_origin)

            hh = PendingHousehold.objects.create(
                registration_data_import=rdi, program=rdi.program, business_area=rdi.business_area, **household_data
            )
            for member_data in members:
                self.save_member(rdi, hh, member_data)
                totals.individuals += 1
        return totals
