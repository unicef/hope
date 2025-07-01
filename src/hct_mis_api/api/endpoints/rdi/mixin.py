import base64
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from django.core.files.uploadedfile import SimpleUploadedFile

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    HEAD,
    NON_BENEFICIARY,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    DocumentType,
    Household,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.payment.models import (
    AccountType,
    FinancialInstitution,
    PendingAccount,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)


def get_photo_from_stream(stream: Optional[str]) -> Optional[SimpleUploadedFile]:
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
    def save_document(self, member: PendingIndividual, doc: Dict) -> None:
        PendingDocument.objects.create(
            document_number=doc["document_number"],
            photo=get_photo_from_stream(doc.get("image", None)),
            individual=member,
            country=Country.objects.get(iso_code2=doc["country"]),
            type=DocumentType.objects.get(key=doc["type"]),
            program=member.program,
        )


class AccountMixin:
    def save_account(self, member: PendingIndividual, doc: Dict) -> None:
        financial_institution_id = doc.pop("financial_institution", None)
        PendingAccount.objects.create(
            individual=member,
            number=doc.pop("number", None),
            unique_key=doc.pop("unique_key", None),
            account_type=AccountType.objects.get(key=doc.pop("account_type")),
            financial_institution=FinancialInstitution.objects.filter(id=financial_institution_id).first(),
            data={**doc.pop("data"), **doc},
        )


class PhotoMixin:
    @staticmethod
    def get_photo(photo: Optional[str]) -> Optional[SimpleUploadedFile]:
        if photo:
            data = photo.removeprefix("data:image/png;base64,")
            p = get_photo_from_stream(data)
            return p
        return None


class HouseholdUploadMixin(DocumentMixin, AccountMixin, PhotoMixin):
    def _manage_collision(
        self, household: Household, registration_data_import: RegistrationDataImport
    ) -> Optional[str]:
        """
        Detects collisions in the provided households data against the existing population.
        """
        program = registration_data_import.program
        if not program.collision_detection_enabled or not program.collision_detector:
            return None
        colision_detector = program.collision_detector
        household_id = colision_detector.detect_collision(household)
        return household_id

    def save_member(self, rdi: RegistrationDataImport, hh: PendingHousehold, member_data: Dict) -> PendingIndividual:
        photo = self.get_photo(member_data.pop("photo", None))
        documents = member_data.pop("documents", [])
        accounts = member_data.pop("accounts", [])
        member_of = None
        if member_data["relationship"] not in (RELATIONSHIP_UNKNOWN, NON_BENEFICIARY):
            member_of = hh
        member_data["flex_fields"] = populate_pdu_with_null_values(rdi.program, member_data.get("flex_fields", None))
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

    def save_households(self, rdi: RegistrationDataImport, households_data: List[Dict]) -> Totals:
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
                registration_data_import=rdi, program=rdi.program, business_area=rdi.business_area, **household_data
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
