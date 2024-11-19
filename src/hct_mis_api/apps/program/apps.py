from django.apps import AppConfig


class ProgramConfig(AppConfig):
    name = "hct_mis_api.apps.program"
    verbose_name = "Programme"

    def ready(self) -> None:
        from hct_mis_api.apps.grievance import signals as grievance_signals
        from hct_mis_api.apps.household import signals as household_signals
        from hct_mis_api.apps.program import signals as program_signals
        from hct_mis_api.apps.program.signals import adjust_program_size
        from hct_mis_api.apps.registration_datahub import signals as rdi_signals

        rdi_signals.rdi_merged.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance.program), weak=False
        )
        grievance_signals.individual_added.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance.program), weak=False
        )
        program_signals.program_copied.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance), weak=False
        )

        household_signals.household_deleted.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance.program), weak=False
        )
        household_signals.household_withdrawn.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance.program), weak=False
        )
        household_signals.individual_withdrawn.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance.program), weak=False
        )
        household_signals.individual_deleted.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance.program), weak=False
        )
        grievance_signals.individual_marked_as_duplicated.connect(
            lambda sender, instance, **kwargs: adjust_program_size(instance.program), weak=False
        )
