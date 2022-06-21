import logging
from typing import List

from hct_mis_api.apps.registration_datahub.models import Record
from hct_mis_api.apps.registration_datahub.templatetags.smart_register import is_image

logger = logging.getLogger(__name__)


def extract(records_ids: List[int], raise_exception=False):
    def _filter(d):
        if isinstance(d, list):
            return [_filter(v) for v in d]
        elif isinstance(d, dict):
            return {k: _filter(v) for k, v in d.items()}
        elif is_image(d):
            return "::image::"
        else:
            return d

    for record_id in records_ids:
        record = Record.objects.get(pk=record_id)
        try:
            record.data = _filter(record.get_data())

            individuals = record.data.get("individuals", {})
            collectors = [individual for individual in individuals if individual.get("role_i_c", "n") == "y"]
            heads = [individual for individual in individuals if individual.get("relationship_i_c") == "head"]

            record.data["w_counters"] = {
                "individuals_num": len(individuals),
                "collectors_num": len(collectors),
                "head": len(heads),
                "valid_phones": len([individual for individual in individuals if individual.get("phone_no_i_c")]),
                "valid_taxid": len([head for head in heads if head.get("tax_id_no_i_c") and head.get("bank_account")]),
                "valid_payment": len(
                    [
                        individual
                        for individual in individuals
                        if individual.get("tax_id_no_i_c") and individual.get("bank_account")
                    ]
                ),
                "birth_certificate": len(
                    [
                        individual
                        for individual in individuals
                        if individual.get("birth_certificate_picture") == "::image::"
                    ]
                ),
                "disability_certificate_match": (
                    len(
                        [
                            individual
                            for individual in individuals
                            if individual.get("disability_certificate_picture") == "::image::"
                        ]
                    )
                    == len([individual for individual in individuals if individual.get("disability_i_c") == "y"])
                ),
                "collector_bank_account": len([individual.get("bank_account") for individual in collectors]) > 0,
            }
            record.save()
        except Exception as e:
            if raise_exception:
                raise
            logger.exception(e)
