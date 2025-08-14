from django.apps import AppConfig


class Config(AppConfig):
    name = "hope.contrib.aurora"

    def ready(self) -> None:
        import hope.contrib.aurora.signals  # noqa: F401
        from hope.contrib.aurora.rdi import registry
        from hope.contrib.aurora.services.czech_republic_flex_registration_service import (
            CzechRepublicFlexRegistration,
        )
        from hope.contrib.aurora.services.generic_registration_service import (
            GenericRegistrationService,
        )
        from hope.contrib.aurora.services.nigeria_people_registration_service import (
            NigeriaPeopleRegistrationService,
        )
        from hope.contrib.aurora.services.people_registration_service import (
            PeopleRegistrationService,
        )
        from hope.contrib.aurora.services.sri_lanka_flex_registration_service import (
            SriLankaRegistrationService,
        )
        from hope.contrib.aurora.services.ukraine_flex_registration_service import (
            Registration2024,
            UkraineBaseRegistrationService,
            UkraineRegistrationService,
        )

        registry.register(GenericRegistrationService)
        registry.register(PeopleRegistrationService)
        registry.register(SriLankaRegistrationService)
        registry.register(UkraineBaseRegistrationService)
        registry.register(UkraineRegistrationService)
        registry.register(CzechRepublicFlexRegistration)
        registry.register(Registration2024)
        registry.register(NigeriaPeopleRegistrationService)
