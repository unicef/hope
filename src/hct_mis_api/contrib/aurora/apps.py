from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.contrib.aurora"

    def ready(self) -> None:
        import hct_mis_api.contrib.aurora.signals  # noqa: F401
        from hct_mis_api.contrib.aurora.rdi import registry
        from hct_mis_api.contrib.aurora.services.czech_republic_flex_registration_service import (
            CzechRepublicFlexRegistration,
        )
        from hct_mis_api.contrib.aurora.services.generic_registration_service import (
            GenericRegistrationService,
        )
        from hct_mis_api.contrib.aurora.services.nigeria_people_registration_service import (
            NigeriaPeopleRegistrationService,
        )
        from hct_mis_api.contrib.aurora.services.people_registration_service import (
            PeopleRegistrationService,
        )
        from hct_mis_api.contrib.aurora.services.sri_lanka_flex_registration_service import (
            SriLankaRegistrationService,
        )
        from hct_mis_api.contrib.aurora.services.ukraine_flex_registration_service import (
            Registration2024,
            UkraineBaseRegistrationService,
            UkraineRegistrationService,
        )

        from . import admin  # noqa

        registry.register(GenericRegistrationService)
        registry.register(PeopleRegistrationService)
        registry.register(SriLankaRegistrationService)
        registry.register(UkraineBaseRegistrationService)
        registry.register(UkraineRegistrationService)
        registry.register(CzechRepublicFlexRegistration)
        registry.register(Registration2024)
        registry.register(NigeriaPeopleRegistrationService)
