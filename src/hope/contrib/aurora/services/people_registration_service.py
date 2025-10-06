from hope.contrib.aurora.services.generic_registration_service import (
    GenericRegistrationService,
)


class PeopleRegistrationService(GenericRegistrationService):
    master_detail = False
