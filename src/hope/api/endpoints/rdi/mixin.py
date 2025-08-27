import base64
import logging
from dataclasses import dataclass

from django.core.files.uploadedfile import SimpleUploadedFile

from hope.models.country import Country
from hope.models.household import (
    HEAD,
    NON_BENEFICIARY,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
    PendingHousehold,
)
from hope.models.document import PendingDocument
from hope.models.individual import PendingIndividual
from hope.models.document_type import DocumentType
from hope.models.account import PendingAccount
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.models.registration_data_import import RegistrationDataImport

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


class DocumentMixin:
    @staticmethod
    def save_document(member: PendingIndividual, doc: dict) -> None:
        PendingDocument.objects.create(
            document_number=doc["document_number"],
            photo=get_photo_from_stream(doc.get("image")),
            individual=member,
            country=Country.objects.get(iso_code2=doc["country"]),
            type=DocumentType.objects.get(key=doc["type"]),
            program=member.program,
        )


class AccountMixin:
    @staticmethod
    def save_account(member: PendingIndividual, doc: dict) -> None:
        PendingAccount.objects.create(individual=member, **doc)


class PhotoMixin:
    @staticmethod
    def get_photo(photo: str | None) -> SimpleUploadedFile | None:
        if photo:
            data = photo.removeprefix("data:image/png;base64,")
            return get_photo_from_stream(data)
        return None


class HouseholdUploadMixin(DocumentMixin, AccountMixin, PhotoMixin):
    def _manage_collision(self, household: Household, registration_data_import: RegistrationDataImport) -> str | None:
        """Detect collisions in the provided households data against the existing population."""
        program = registration_data_import.program
        if not program.collision_detection_enabled or not program.collision_detector:
            return None
        colision_detector = program.collision_detector
        return colision_detector.detect_collision(household)

    def save_member(self, rdi: RegistrationDataImport, hh: PendingHousehold, member_data: dict) -> PendingIndividual:
        photo = self.get_photo(member_data.pop("photo", None))
        documents = member_data.pop("documents", [])
        accounts = member_data.pop("accounts", [])
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
            photo=photo,
            **member_data,
        )
        for doc in documents:
            self.save_document(ind, doc)
        for account in accounts:
            self.save_account(ind, account)
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
        household_ids_to_add_extra_rdis = []
        for household_data in households_data:
            totals.households += 1
            members: list[dict] = household_data.pop("members")
            if country := household_data.get("country"):
                household_data["country"] = Country.objects.get(iso_code2=country)

            if country_origin := household_data.get("country_origin"):
                household_data["country_origin"] = Country.objects.get(iso_code2=country_origin)

            hh = PendingHousehold(
                registration_data_import=rdi,
                program=rdi.program,
                business_area=rdi.business_area,
                **household_data,
            )

            if collided_household_id := self._manage_collision(hh, rdi):
                totals.individuals += len(members)
                household_ids_to_add_extra_rdis.append(collided_household_id)
                continue

            hh.save()
            for member_data in members:
                self.save_member(rdi, hh, member_data)
                totals.individuals += 1
        rdi.extra_hh_rdis.add(*household_ids_to_add_extra_rdis)
        return totals
