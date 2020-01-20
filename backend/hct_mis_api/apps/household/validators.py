from PIL import Image
from django.core.exceptions import ValidationError

from core.validators import BaseValidator


class HouseholdValidator(BaseValidator):

    def validate_consent(self, files, *args, **kwargs):
        if self.__name__.startswith('Create') and not files:
            raise ValidationError('Consent image is required.')

        if len(files) > 1:
            raise ValidationError('You can upload only one image.')

        for name, file in files.items():
            import ipdb; ipdb.set_trace()