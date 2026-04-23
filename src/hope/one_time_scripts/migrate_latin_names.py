from hope.apps.household.utils import to_latin
from hope.models import Individual

BATCH_SIZE = 500


def migrate_to_latin_names() -> None:
    qs = Individual.objects.all().iterator(chunk_size=BATCH_SIZE)
    to_update = []

    # TODO: add pagination maybe

    for ind in qs:
        if ind.full_name and not ind.full_name_latin:
            ind.full_name_latin = to_latin(ind.full_name)
        if ind.given_name and not ind.given_name_latin:
            ind.given_name_latin = to_latin(ind.given_name)
        if ind.middle_name and not ind.middle_name_latin:
            ind.middle_name_latin = to_latin(ind.middle_name)
        if ind.family_name and not ind.family_name_latin:
            ind.family_name_latin = to_latin(ind.family_name)

        to_update.append(ind)

    Individual.objects.bulk_update(to_update, fields=[
        "full_name_latin", "given_name_latin", "middle_name_latin", "family_name_latin"
    ], batch_size=BATCH_SIZE)
