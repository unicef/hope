import logging

from .base import DjangoOperator


log = logging.getLogger(__name__)


class TestConnectionOperator(DjangoOperator):
    def try_execute(self, context):
        from hct_mis_api.apps.registration_datahub.fixtures import (
            RegistrationDataImportDatahubFactory,
        )
        from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub

        rdi_dh = RegistrationDataImportDatahubFactory()

        log.info(f"RDI-Datahub name: {rdi_dh.name}")

        assert (
            RegistrationDataImportDatahub.objects.get(id=rdi_dh.id).name
            == rdi_dh.name
        )

        rdi_dh.delete()
