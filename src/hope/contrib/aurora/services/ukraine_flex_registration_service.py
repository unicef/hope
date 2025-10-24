from typing import TYPE_CHECKING, Any
import uuid

from django.core.exceptions import ValidationError
from django.forms import modelform_factory

from hope.apps.core.utils import (
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
    build_arg_dict_from_dict,
    build_flex_arg_dict_from_list_if_exists,
)
from hope.apps.geo.models import Area, Country
from hope.apps.household.forms import DocumentForm, IndividualForm
from hope.apps.household.models import (
    BLANK,
    DISABLED,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_DRIVERS_LICENSE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO,
    IDENTIFICATION_TYPE_TAX_ID,
    NOT_DISABLED,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from hope.apps.registration_data.models import RegistrationDataImport
from hope.contrib.aurora.services.base_flex_registration_service import (
    BaseRegistrationService,
)

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from hope.apps.account.models import Role


class UkraineBaseRegistrationService(BaseRegistrationService):
    INDIVIDUAL_MAPPING_DICT = {
        "given_name": "given_name_i_c",
        "family_name": "family_name_i_c",
        "middle_name": "patronymic",
        "birth_date": "birth_date",
        "sex": "gender_i_c",
        "relationship": "relationship_i_c",
        "disability": "disability_i_c",
        "disability_certificate_picture": "disability_certificate_picture",
        "phone_no": "phone_no_i_c",
        "role": "role_i_c",
        "email": "email",
    }

    HOUSEHOLD_MAPPING_DICT = {
        "residence_status": "residence_status_h_c",
        "admin1": "admin1_h_c",
        "admin2": "admin2_h_c",
        "size": "size_h_c",
    }

    DOCUMENT_MAPPING_KEY_DICT = {
        IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]: (
            "national_id_no_i_c_1",
            "national_id_picture",
        ),
        IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT]: (
            "international_passport_i_c",
            "international_passport_picture",
        ),
        IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_DRIVERS_LICENSE]: (
            "drivers_license_no_i_c",
            "drivers_license_picture",
        ),
        IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]: (
            "birth_certificate_no_i_c",
            "birth_certificate_picture",
        ),
        IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO]: (
            "residence_permit_no_i_c",
            "residence_permit_picture",
        ),
        IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID]: (
            "tax_id_no_i_c",
            "tax_id_picture",
        ),
    }

    def create_household_for_rdi_household(self, record: Any, registration_data_import: RegistrationDataImport) -> None:
        individuals: list[PendingIndividual] = []
        documents: list[PendingDocument] = []
        record_data_dict = record.get_data()
        household_dict = record_data_dict.get("household", [])[0]
        individuals_array = record_data_dict.get("individuals", [])
        enumerator_rec_id = record_data_dict.get("enumerator")

        if not self._has_head(individuals_array):
            self._set_default_head_of_household(individuals_array)

        self.validate_household(individuals_array)

        household_data = self._prepare_household_data(household_dict, record, registration_data_import)
        if not household_data.get("size"):
            household_data["size"] = len(individuals_array)
        if enumerator_rec_id:
            household_data["enumerator_rec_id"] = enumerator_rec_id
        household = self._create_object_and_validate(household_data, PendingHousehold)
        household.set_admin_areas()

        household.detail_id = record.source_id
        household.save(update_fields=("detail_id", "admin1", "admin2", "admin3", "admin4"))

        for index, individual_dict in enumerate(individuals_array):
            try:
                individual_data = self._prepare_individual_data(individual_dict, household, registration_data_import)
                role = individual_data.pop("role")
                phone_no = individual_data.pop("phone_no", "")

                individual: PendingIndividual = self._create_object_and_validate(
                    individual_data, PendingIndividual, IndividualForm
                )
                individual.disability_certificate_picture = individual_data.get("disability_certificate_picture")
                individual.phone_no = phone_no
                individual.detail_id = record.source_id
                individual.save()

                self._create_role(role, individual, household)
                individuals.append(individual)

                if individual.relationship == HEAD:
                    household.head_of_household = individual
                    household.save(update_fields=("head_of_household",))
                documents.extend(self._prepare_documents(individual_dict, individual))
            except ValidationError as e:
                raise ValidationError({f"individual nr {index + 1}": [str(e)]}) from e

        PendingDocument.objects.bulk_create(documents)

    def _set_default_head_of_household(self, individuals_array: "QuerySet") -> None:
        for individual_data in individuals_array:
            if individual_data.get("role_i_c") == "y":
                individual_data["relationship_i_c"] = "head"
                break

    def _create_role(self, role: "Role", individual: PendingIndividual, household: PendingHousehold) -> None:
        if role == "y":
            defaults = {"individual": individual, "household": household}
            if PendingIndividualRoleInHousehold.objects.filter(household=household, role=ROLE_PRIMARY).count() == 0:
                PendingIndividualRoleInHousehold.objects.create(**defaults, role=ROLE_PRIMARY)
            elif PendingIndividualRoleInHousehold.objects.filter(household=household, role=ROLE_ALTERNATE).count() == 0:
                PendingIndividualRoleInHousehold.objects.create(**defaults, role=ROLE_ALTERNATE)
            else:
                raise ValidationError("There should be only two collectors!")

    def _prepare_household_data(
        self,
        household_dict: dict,
        record: Any,
        registration_data_import: RegistrationDataImport,
    ) -> dict:
        household_data = {
            "registration_data_import": registration_data_import,
            "program": registration_data_import.program,
            "first_registration_date": record.timestamp,
            "last_registration_date": record.timestamp,
            "country_origin": Country.objects.get(iso_code2="UA"),
            "country": Country.objects.get(iso_code2="UA"),
            "consent": True,
            "size": household_dict.get("size_h_c"),
            "business_area": registration_data_import.business_area,
            "residence_status": household_dict.get("residence_status_h_c", BLANK),
        }

        admin1 = household_dict.get("admin1_h_c")
        admin2 = household_dict.get("admin2_h_c")
        admin3 = household_dict.get("admin2_h_c")
        admin4 = household_dict.get("admin2_h_c")

        household_data["admin1"] = str(Area.objects.get(p_code=admin1).id) if admin1 else None
        household_data["admin2"] = str(Area.objects.get(p_code=admin2).id) if admin2 else None
        household_data["admin3"] = str(Area.objects.get(p_code=admin3).id) if admin3 else None
        household_data["admin4"] = str(Area.objects.get(p_code=admin4).id) if admin4 else None

        if residence_status := household_data.get("residence_status"):
            household_data["residence_status"] = residence_status.upper()

        return household_data

    def _prepare_individual_data(
        self,
        individual_dict: dict,
        household: PendingHousehold,
        registration_data_import: RegistrationDataImport,
    ) -> dict:
        individual_data = dict(
            **build_arg_dict_from_dict(individual_dict, self.INDIVIDUAL_MAPPING_DICT),
            household=str(household.pk),
            program=registration_data_import.program,
            registration_data_import=registration_data_import,
            first_registration_date=household.first_registration_date,
            last_registration_date=household.last_registration_date,
            business_area=registration_data_import.business_area,
        )
        disability = individual_data.get("disability", "n")
        disability_certificate_picture = individual_data.get("disability_certificate_picture")
        if disability == "y" or disability_certificate_picture:
            individual_data["disability"] = DISABLED
        else:
            individual_data["disability"] = NOT_DISABLED

        if relationship := individual_data.get("relationship"):
            individual_data["relationship"] = relationship.upper()
        if sex := individual_data.get("sex"):
            individual_data["sex"] = sex.upper()

        if phone_no := individual_data.get("phone_no"):
            if phone_no.startswith("0") and not phone_no.startswith("00"):
                phone_no = phone_no[1:]
            if not phone_no.startswith("+380"):
                individual_data["phone_no"] = f"+380{phone_no}"
        else:
            individual_data["phone_no"] = ""

        if disability_certificate_picture:
            certificate_picture = f"CERTIFICATE_PICTURE_{uuid.uuid4()}"
            disability_certificate_picture = self._prepare_picture_from_base64(
                disability_certificate_picture, certificate_picture
            )
            individual_data["disability_certificate_picture"] = disability_certificate_picture

        given_name = individual_data.get("given_name")
        middle_name = individual_data.get("middle_name")
        family_name = individual_data.get("family_name")

        individual_data["full_name"] = " ".join(filter(None, [given_name, middle_name, family_name]))

        return individual_data

    def _prepare_documents(self, individual_dict: dict, individual: PendingIndividual) -> list[PendingDocument]:
        documents = []

        for document_key_string, (
            document_number_field_name,
            picture_field_name,
        ) in UkraineRegistrationService.DOCUMENT_MAPPING_KEY_DICT.items():
            document_number = individual_dict.get(document_number_field_name)
            certificate_picture = individual_dict.get(picture_field_name, "")

            if not document_number and not certificate_picture:
                continue

            document_number = document_number or f"ONLY_PICTURE_{uuid.uuid4()}"

            certificate_picture = self._prepare_picture_from_base64(certificate_picture, document_number)

            document_type = DocumentType.objects.get(key=document_key_string)
            document_kwargs = {
                "country": Country.objects.get(iso_code2="UA"),
                "type": document_type,
                "document_number": document_number,
                "individual": individual.pk,
                "program": individual.program,
            }
            ModelClassForm = modelform_factory(PendingDocument, form=DocumentForm, fields=list(document_kwargs.keys()))  # noqa
            form = ModelClassForm(data=document_kwargs)
            if not form.is_valid():
                raise ValidationError(form.errors)
            document_kwargs["individual"] = individual
            document = PendingDocument(photo=certificate_picture, **document_kwargs)
            documents.append(document)

        return documents

    def validate_household(self, individuals_array: list[PendingIndividual]) -> None:
        if not individuals_array:
            raise ValidationError("Household should has at least one individual")

        has_head = self._has_head(individuals_array)
        if not has_head:
            raise ValidationError("Household should has at least one Head of Household")

    def _has_head(self, individuals_array: list[PendingIndividual]) -> bool:
        return any(
            individual_data.get(
                "relationship_i_c",
            )
            == "head"
            for individual_data in individuals_array
        )


class UkraineRegistrationService(UkraineBaseRegistrationService):
    HOUSEHOLD_MAPPING_DICT = {
        "admin1": "admin1_h_c",
        "admin2": "admin2_h_c",
        "admin3": "admin3_h_c",
        "admin4": "admin4_h_c",
    }


class Registration2024(UkraineBaseRegistrationService):
    INDIVIDUAL_FLEX_FIELDS: list[str] = ["low_income_hh_h_f", "single_headed_hh_h_f"]

    def _prepare_individual_data(
        self,
        individual_dict: dict,
        household: PendingHousehold,
        registration_data_import: RegistrationDataImport,
    ) -> dict:
        individual_data = super()._prepare_individual_data(individual_dict, household, registration_data_import)
        individual_data["flex_fields"] = build_flex_arg_dict_from_list_if_exists(
            individual_dict, self.INDIVIDUAL_FLEX_FIELDS
        )
        return individual_data
