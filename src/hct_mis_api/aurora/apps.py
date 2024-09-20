from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.aurora"

    def ready(self) -> None:
        from hct_mis_api.aurora.rdi import registry
        from hct_mis_api.aurora.services.czech_republic_flex_registration_service import (
            CzechRepublicFlexRegistration,
        )
        from hct_mis_api.aurora.services.generic_registration_service import (
            GenericRegistrationService,
        )
        from hct_mis_api.aurora.services.sri_lanka_flex_registration_service import (
            SriLankaRegistrationService,
        )
        from hct_mis_api.aurora.services.ukraine_flex_registration_service import (
            Registration2024,
            UkraineBaseRegistrationService,
            UkraineRegistrationService,
        )

        from . import admin  # noqa

        registry.register(GenericRegistrationService)
        registry.register(SriLankaRegistrationService)
        registry.register(UkraineBaseRegistrationService)
        registry.register(UkraineRegistrationService)
        registry.register(CzechRepublicFlexRegistration)
        registry.register(Registration2024)
