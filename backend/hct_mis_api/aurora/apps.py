from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.aurora"

    def ready(self) -> None:
        from hct_mis_api.apps.registration_datahub.services.czech_republic_flex_registration_service import (
            CzechRepublicFlexRegistration,
        )
        from hct_mis_api.apps.registration_datahub.services.sri_lanka_flex_registration_service import (
            SriLankaRegistrationService,
        )
        from hct_mis_api.apps.registration_datahub.services.ukraine_flex_registration_service import (
            UkraineBaseRegistrationService,
            UkraineRegistrationService,
        )
        from hct_mis_api.aurora.rdi import registry

        from . import admin  # noqa

        registry.register(SriLankaRegistrationService)
        registry.register(UkraineBaseRegistrationService)
        registry.register(UkraineRegistrationService)
        registry.register(CzechRepublicFlexRegistration)
