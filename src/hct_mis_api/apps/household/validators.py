import logging
from typing import IO, Any, List

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator

logger = logging.getLogger(__name__)


class HouseholdValidator(BaseValidator):
    def validate_consent(self, files: List[IO], *args: Any, **kwargs: Any) -> None:
        if self.__name__.startswith("Create") and not files:
            logger.error("Consent image is required.")
            raise ValidationError("Consent image is required.")

        if len(files) > 1:
            logger.error("You can upload only one image.")
            raise ValidationError("You can upload only one image.")

        file = next(iter(files.values()))

        if file and "image" not in file.content_type:
            logger.error("File is not a valid image")
            raise ValidationError("File is not a valid image")
