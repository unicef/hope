from functools import reduce

from django.db import transaction

from .base import DjangoOperator


class MergeRegistrationImportDataOperator(DjangoOperator):
    def merge_household(
        self, imported_household, household_values, registration_obj
    ):
        from household.models import Household

        imported_individuals_as_values = imported_household.individuals.values(
            "id",
            "photo",
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "relationship",
            "role",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "phone_no",
            "phone_no_alternative",
            "disability",
            "flex_fields",
        )

        def id_reducer(old, new):
            old[new.id] = new
            return old

        imported_individuals_as_values_id_dict = reduce(
            id_reducer, imported_household.individuals.all(), {}
        )
        individuals_to_add = []
        del household_values["id"]
        household = Household(**{**household_values})
        household.registration_data_import = registration_obj
        self.merge_admin_area(
            imported_household, household_values, household
        )
        for individual_values in imported_individuals_as_values:
            imported_individual = imported_individuals_as_values_id_dict[
                individual_values.get("id")
            ]
            individual = self.merge_individual(
                imported_individual,
                individual_values,
                household,
                registration_obj,
            )
            if individual_values["relationship"] == "HEAD":
                household.head_of_household = individual
            individuals_to_add.append(individual)
        return household, individuals_to_add

    def merge_individual(
        self,
        imported_individual,
        individual_values,
        household,
        registration_obj,
    ):
        from household.models import Individual

        del individual_values["id"]
        individual = Individual(**{**individual_values})
        individual.household = household
        individual.registration_data_import = registration_obj
        self.merge_individual_document(
            imported_individual, individual_values, individual
        )
        return individual

    def merge_individual_document(
        self, imported_individual, individual_values, individual,
    ):
        from household.models import Document, DocumentType

        documents_to_create = []
        for imported_document in imported_individual.documents.all():
            document_type = DocumentType.objects.get(
                country=imported_document.type.country,
                label=imported_document.type.label,
            )
            document = Document(
                document_number=imported_document.document_number,
                type=document_type,
                individual=individual,
            )
            documents_to_create.append(document)
        Document.objects.bulk_create(documents_to_create)

    def merge_admin_area(
        self, imported_household, household_values, household,
    ):
        from core.models import AdminArea

        admin1 = imported_household.admin1
        admin2 = imported_household.admin2
        try:
            if admin2 is not None:
                admin_area = AdminArea.objects.get(title=admin2)
                household.admin_area = admin_area
                return
            if admin1 is not None:
                admin_area = AdminArea.objects.get(title=admin1)
                household.admin_area = admin_area
                return
        except AdminArea.DoesNotExist:
            print("does not exsit")

    @transaction.atomic()
    def execute(self, context, **kwargs):
        from registration_data.models import RegistrationDataImport
        from household.models import Individual, Household
        from registration_datahub.models import (
            RegistrationDataImportDatahub,
            ImportedIndividual,
            ImportedHousehold,
        )

        dag_run = context["dag_run"]
        config_vars = dag_run.conf
        registration_data_import_id = config_vars.get(
            "registration_data_import_id"
        )
        obj_hub = RegistrationDataImportDatahub.objects.get(
            hct_id=registration_data_import_id,
        )

        obj_hct = RegistrationDataImport.objects.get(
            id=registration_data_import_id,
        )

        # move individuals and households to hct db
        imported_households = ImportedHousehold.objects.filter(
            registration_data_import=obj_hub,
        )

        def id_reducer(old, new):
            old[new.id] = new
            return old

        imported_households_id_dict = reduce(
            id_reducer, imported_households, {}
        )
        imported_households.all()
        imported_individuals = ImportedIndividual.objects.filter(
            registration_data_import=obj_hub,
        )

        imported_households_as_values = imported_households.values(
            "id",
            "consent",
            "residence_status",
            "country_origin",
            "size",
            "address",
            "country",
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_adults_count",
            "pregnant_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_adults_count",
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_adults_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_adults_disabled_count",
            "registration_date",
            "flex_fields",
        )
        households_to_add = []
        individuals_to_add = []
        for hh_values in imported_households_as_values:
            imported_household = imported_households_id_dict[
                hh_values.get("id")
            ]
            (household, hh_individuals_to_add) = self.merge_household(
                imported_household, hh_values, obj_hct
            )
            households_to_add.append(household)
            individuals_to_add.extend(hh_individuals_to_add)
        Individual.objects.bulk_create(individuals_to_add)
        Household.objects.bulk_create(households_to_add)

        # TODO: update household head and representative

        # cleanup datahub
        # imported_households.delete()
        # imported_individuals.delete()

        obj_hct.status = "MERGED"
        obj_hct.save()
