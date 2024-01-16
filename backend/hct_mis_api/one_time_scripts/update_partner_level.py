import logging

from hct_mis_api.apps.account.models import Partner

logger = logging.getLogger(__name__)


def update_partner_level() -> None:
    logger.info("Update Partner level")
    before_update_list = list(Partner.objects.all().values_list("level", flat=True))
    logger.info(f"Level list before update {before_update_list}")

    level_0 = Partner.objects.filter(parent__isnull=True).update(level=0)
    level_1 = Partner.objects.filter(parent__isnull=False).update(level=1)

    logger.info(f"Updated level_0/level_1: {level_0}/{level_1}")

    after_update_list = list(Partner.objects.all().values_list("level", flat=True))
    logger.info(f"Level list after update {after_update_list}")
