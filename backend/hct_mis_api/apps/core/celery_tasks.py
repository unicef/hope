import csv
import logging
from datetime import datetime
from functools import wraps

from django.db import transaction

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import StorageFile, XLSXKoboTemplate
from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
    KoboRetriableError,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_TAX_ID,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


class transaction_celery_task:  # used as decorator
    def __init__(self, *args, **kwargs):
        self.task_args = args
        self.task_kwargs = kwargs

    def __call__(self, func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                with transaction.atomic():
                    return func(*args, **kwargs)
            except Exception as e:
                logger.error(e)

        task_func = app.task(*self.task_args, **self.task_kwargs)(wrapper_func)
        return task_func


@app.task(bind=True, default_retry_delay=60)
@log_start_and_end
@sentry_tags
def upload_new_kobo_template_and_update_flex_fields_task_with_retry(self, xlsx_kobo_template_id):
    try:
        from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
            UploadNewKoboTemplateAndUpdateFlexFieldsTask,
        )

        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError as exc:
        from datetime import timedelta

        from django.utils import timezone

        one_day_earlier_time = timezone.now() - timedelta(days=1)
        if exc.xlsx_kobo_template_object.first_connection_failed_time > one_day_earlier_time:
            logger.exception(exc)
            raise self.retry(exc=exc)
        else:
            exc.xlsx_kobo_template_object.status = XLSXKoboTemplate.UNSUCCESSFUL
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def upload_new_kobo_template_and_update_flex_fields_task(xlsx_kobo_template_id):
    try:
        from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
            UploadNewKoboTemplateAndUpdateFlexFieldsTask,
        )

        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError:
        upload_new_kobo_template_and_update_flex_fields_task_with_retry.delay(xlsx_kobo_template_id)
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@sentry_tags
def create_target_population_task(storage_id, program_id, tp_name):
    storage_obj = StorageFile.objects.get(id=storage_id)
    program = Program.objects.get(id=program_id)

    business_area = storage_obj.business_area

    passport_type = DocumentType.objects.get(type=IDENTIFICATION_TYPE_NATIONAL_PASSPORT)
    tax_type = DocumentType.objects.get(type=IDENTIFICATION_TYPE_TAX_ID)

    first_registration_date = datetime.now()
    last_registration_date = first_registration_date

    family_ids = set()
    individuals = []
    documents = []
    bank_infos = []

    with open(storage_obj.file.path, encoding="KOI8-U") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            family_id = row["ID_FAM"]

            iban = row["IBAN"]
            tax_id = row["N_ID"]
            passport_id = row["PASSPORT"]

            individual_data = {
                "given_name": row["NAME"],
                "middle_name": row["PATRONYMIC"],
                "family_name": row["SURNAME"],
                "birth_date": datetime.strptime(row["BDATE"], "%d.%m.%Y").date(),
                "phone_no": row["PHONе"],
                "business_area": business_area,
                "first_registration_date": first_registration_date,
                "last_registration_date": last_registration_date,
            }

            if family_id in family_ids:
                individuals.append(Individual(**individual_data, household=Household.objects.get(family_id=family_id)))
            else:
                individual = Individual.objects.create(**individual_data)

                household = Household.objects.create(
                    head_of_household=individual,
                    business_area=business_area,
                    first_registration_date=first_registration_date,
                    last_registration_date=last_registration_date,
                    family_id=family_id,
                    storage_obj=storage_obj,
                )

                individual.household = household
                individual.save()

                family_ids.add(family_id)

            passport = Document(
                document_number=passport_id, type=passport_type, individual=individual, status=Document.STATUS_VALID
            )

            tax = Document(document_number=tax_id, type=tax_type, individual=individual, status=Document.STATUS_VALID)

            bank_account_info = BankAccountInfo(bank_account_number=iban, individual=individual)

            documents.append(passport)
            documents.append(tax)

            bank_infos.append(bank_account_info)

    Individual.objects.bulk_create(individuals)

    Document.objects.bulk_create(documents)
    BankAccountInfo.objects.bulk_create(bank_infos)

    households = Household.objects.filter(family_id__in=list(family_ids))
    households_ids = households.values_list("id", flat=True)

    for household in households:
        household.size = Individual.objects.filter(household=household).count()
    Household.objects.bulk_update(households, ["size"])

    target_population = TargetPopulation.objects.create(
        name=tp_name,
        created_by=storage_obj.created_by,
        program=program,
        total_households_count=len(households),
        total_individuals_count=Individual.objects.filter(household_id__in=list(households_ids)).count(),
        status=TargetPopulation.STATUS_LOCKED,
        business_area=business_area,
        storage_file=storage_obj,
    )

    target_population.households.set(households)
