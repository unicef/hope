import logging

from .base import DjangoOperator


log = logging.getLogger(__name__)


class TestConnectionOperator(DjangoOperator):

    def execute(self, context):
        from household.models import Household
        from household.fixtures import HouseholdFactory
        from registration_datahub.models import ImportedHousehold
        from registration_datahub.fixtures import ImportedHouseholdFactory

        hh = HouseholdFactory()

        log.info(f'Get object Household: {hh.family_size}')
        log.info(f'Household: {hh.address}')

        log.info(f'{Household.objects.get(id=hh.id)}')

        i_hh = ImportedHouseholdFactory()

        log.info(f'Get object ImportedHousehold: {i_hh.family_size}')
        log.info(f'ImportedHousehold: {i_hh.address}')

        log.info(f'{ImportedHousehold.objects.get(id=i_hh.id)}')

        hh.delete()
        i_hh.delete()
